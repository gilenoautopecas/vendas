from django.shortcuts import render, redirect, get_object_or_404
from .models import Venda, ItemVenda
from .forms import VendaForm, ItemVendaForm
from .services import criar_venda, adicionar_item, remover_item
from .queries import total_hoje, listar_vendas_filtradas, vendas_por_dia
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.paginator import Paginator

import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Q
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from core.telegram_utils import enviar_mensagem_telegram

from django.contrib import messages
from django.shortcuts import redirect

from core.services.sync_gdoor import sincronizar_produtos


def importar_produtos_gdoor(request):
    empresa = request.user.perfil.empresa
    total_importados = sincronizar_produtos(empresa)

    empresa.ultima_sincronizacao = now()
    empresa.save(update_fields=["ultima_sincronizacao"])

    messages.success(
        request,
        f"{total_importados} produtos sincronizados do Gdoor."
    )

    return redirect("dashboard")


def formatar_real(valor):
    valor = valor or 0
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"



def imprimir_venda_pdf(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, empresa=request.user.perfil.empresa)
    html_string = render_to_string("venda/pdf_venda.html", {
        "venda": venda,
        "itens": venda.itens.all()
    })

    try:
        from weasyprint import HTML
        pdf = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="venda_{venda.id}.pdf"'
        return response
    except Exception:
        # No Windows (sem libs), retorna o HTML pronto pra imprimir
        return HttpResponse(html_string)


def dashboard(request):
    empresa = request.user.perfil.empresa
    q = request.GET.get("q", "").strip()
    data = request.GET.get("data", "").strip()
    inicio = request.GET.get("inicio", "").strip()
    fim = request.GET.get("fim", "").strip()

    # converter strings -> date
    def to_date(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None

    data_date = to_date(data)
    inicio_date = to_date(inicio)
    fim_date = to_date(fim)

    vendas = listar_vendas_filtradas(
        empresa,
        q=q or None,
        data=data_date,
        inicio=inicio_date,
        fim=fim_date,
        limit=200
    )


    total_hoje = (
        Venda.objects.filter(empresa=empresa, data__date=now().date(), cancelada=False)
        .aggregate(total=Sum("total"))["total"] or 0
    )

    total_filtrado = vendas.aggregate(total=Sum("total"))["total"] or 0
    qtd_filtrado = vendas.count()

    paginator = Paginator(vendas, 10)
    page_number = request.GET.get("page")
    vendas_page = paginator.get_page(page_number)

    ultima_sync = empresa.ultima_sincronizacao
    if ultima_sync:
        delta = now() - ultima_sync
        minutos = int(delta.total_seconds() // 60)
        if minutos < 1:
            sync_label = "agora mesmo"
        elif minutos < 60:
            sync_label = f"há {minutos} min"
        elif minutos < 1440:
            horas = minutos // 60
            sync_label = f"há {horas}h"
        else:
            dias = minutos // 1440
            sync_label = f"há {dias} dia{'s' if dias > 1 else ''}"
    else:
        sync_label = None

    return render(request, "venda/dashboard.html", {
        "total_hoje": total_hoje,
        "total_filtrado": total_filtrado,
        "qtd_filtrado": qtd_filtrado,
        "vendas": vendas_page,
        "q": q,
        "data": data,
        "inicio": inicio,
        "fim": fim,
        "sync_label": sync_label,
    })



def nova_venda(request):
    if request.method == "POST":
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = criar_venda(
                empresa=request.user.perfil.empresa,
                forma_pagamento=form.cleaned_data["forma_pagamento"],
                observacao=form.cleaned_data["observacao"]
            )
            return redirect("editar_venda", venda_id=venda.id)
    else:
        form = VendaForm()

    return render(request, "venda/nova_venda.html", {"form": form})



def editar_venda(request, venda_id):
    empresa = request.user.perfil.empresa
    venda = get_object_or_404(Venda, id=venda_id, empresa=empresa)
    form_item = ItemVendaForm(empresa=empresa)

    if request.method == "POST":
        form_item = ItemVendaForm(request.POST, empresa=empresa)
        if form_item.is_valid():
            adicionar_item(
                venda=venda,
                produto=form_item.cleaned_data["produto"],
                quantidade=form_item.cleaned_data["quantidade"],
                preco_unitario=form_item.cleaned_data["preco_unitario"],
            )
            return redirect("editar_venda", venda_id=venda.id)

    return render(request, "venda/editar_venda.html", {
        "venda": venda,
        "form_item": form_item,
        "itens": venda.itens.all()
    })



def deletar_item(request, item_id):
    item = get_object_or_404(ItemVenda, id=item_id, venda__empresa=request.user.perfil.empresa)
    venda_id = item.venda.id
    remover_item(item)
    return redirect("editar_venda", venda_id=venda_id)


def finalizar_venda_view(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, empresa=request.user.perfil.empresa)

    if not venda.itens.exists():
        return redirect("editar_venda", venda_id=venda.id)

    if not venda.finalizada:
        venda.finalizada = True
        venda.save()

        linhas_itens = []
        for item in venda.itens.select_related("produto").all()[:10]:
            linhas_itens.append(
                f"- {item.produto.nome} x{item.quantidade} = {formatar_real(item.subtotal)}"
            )

        hoje = timezone.localdate()

        total_dia = Venda.objects.filter(
            empresa=venda.empresa,
            data__date=hoje,
            finalizada=True,
            cancelada=False
        ).aggregate(total=Sum("total"))["total"] or 0

        texto = (
            f"🛒 Nova venda finalizada\n\n"
            f"Venda #{venda.id}\n"
            f"Total da venda: {formatar_real(venda.total)}\n"
            f"Pagamento: {venda.get_forma_pagamento_display()}\n"
        )

        if venda.observacao:
            texto += f"Obs: {venda.observacao}\n"

        if linhas_itens:
            texto += "\nItens:\n" + "\n".join(linhas_itens)

        texto += f"\n-----------\n"
        texto += f"\nMontante vendido hoje: {formatar_real(total_dia)}\n"

        enviar_mensagem_telegram(texto)

    return redirect("dashboard")


def cancelar_venda_view(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, empresa=request.user.perfil.empresa)
    venda.delete()
    return redirect("dashboard")


def excluir_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, empresa=request.user.perfil.empresa)
    venda.delete()
    return redirect("dashboard")


def visualizar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, empresa=request.user.perfil.empresa)

    return render(request, "venda/visualizar_venda.html", {
        "venda": venda,
        "itens": venda.itens.all()
    })

# Adicione esta importação no topo do arquivo
from core.models import Produto

# Substitua a sua função produtos() atual por esta:
def produtos(request):
    empresa = request.user.perfil.empresa
    q = request.GET.get("q", "").strip()

    if q:
        # Busca produtos pelo nome (ignorando maiúsculas/minúsculas) ou código gdoor
        lista_produtos = Produto.objects.filter(
            Q(nome__icontains=q) | Q(codigo_gdoor__icontains=q),
            empresa=empresa
        ).order_by("nome")
    else:
        lista_produtos = Produto.objects.filter(empresa=empresa).order_by("nome")

    paginator = Paginator(lista_produtos, 15)
    page_number = request.GET.get("page")
    produtos_page = paginator.get_page(page_number)

    return render(request, "venda/produtos.html", {
        "produtos": produtos_page,
        "q": q,
    })

# Adicione esta nova função para lidar com a edição:
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, empresa=request.user.perfil.empresa)
    
    if request.method == "POST":
        produto.nome = request.POST.get("nome")
        produto.preco_padrao = request.POST.get("preco_padrao")
        produto.ativo = request.POST.get("ativo") == "on"
        produto.save()
        
        messages.success(request, f"Produto '{produto.nome}' atualizado com sucesso!")
        return redirect("produtos")

    return render(request, "venda/editar_produto.html", {
        "produto": produto
    })

def relatorios(request):
    empresa = request.user.perfil.empresa
    hoje = now().date()
    filtro = request.GET.get("filtro", "mes")
    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")

    # Default: último mês
    if filtro == "mes":
        inicio_date = hoje - timedelta(days=30)
        fim_date = hoje
    elif filtro == "semana":
        inicio_date = hoje - timedelta(days=7)
        fim_date = hoje
    elif filtro == "periodo" and inicio and fim:
        inicio_date = datetime.strptime(inicio, "%Y-%m-%d").date()
        fim_date = datetime.strptime(fim, "%Y-%m-%d").date()
    else:
        inicio_date = hoje - timedelta(days=30)
        fim_date = hoje

    dados = vendas_por_dia(empresa, inicio_date, fim_date)

    total_periodo = sum(d["total"] for d in dados)
    dias = [d["dia"].strftime("%d/%m") for d in dados]
    totais = [float(d["total"]) for d in dados]
    quantidades = [d["quantidade"] for d in dados]

    # Totais por forma de pagamento
    totais_pagamento = (
        Venda.objects
        .filter(
            empresa=empresa,
            data__date__range=(inicio_date, fim_date),
            cancelada=False
        )
        .values("forma_pagamento")
        .annotate(
            total=Sum("total"),
            quantidade=Count("id")
        )
    )

    formas_dict = dict(Venda.FORMAS_PAGAMENTO)

    totais_pagamento_formatado = []
    total_pagamentos_geral = 0

    for item in totais_pagamento:
        total_pagamentos_geral += item["total"] or 0

    for item in totais_pagamento:
        total = item["total"] or 0
        percentual = (total / total_pagamentos_geral * 100) if total_pagamentos_geral else 0

        totais_pagamento_formatado.append({
            "forma": formas_dict.get(item["forma_pagamento"]),
            "total": total,
            "quantidade": item["quantidade"],
            "percentual": round(percentual, 2),
        })

    return render(request, "venda/relatorios.html", {
        "dados": dados,
        "dias_json": json.dumps(dias),
        "totais_json": json.dumps(totais),
        "quantidades": quantidades,
        "total_periodo": total_periodo,
        "inicio": inicio_date,
        "fim": fim_date,
        "totais_pagamento": totais_pagamento_formatado,
        "labels_pagamento_json": json.dumps([item["forma"] for item in totais_pagamento_formatado]),
        "valores_pagamento_json": json.dumps([float(item["total"]) for item in totais_pagamento_formatado]),
        "filtro": filtro,
    })



from .services import gerar_grafico_svg
def imprimir_relatorio(request):
    empresa = request.user.perfil.empresa
    hoje = now().date()
    filtro = request.GET.get("filtro", "mes")
    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")

    # Função para converter datas
    def to_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except:
            return None

    # Converter datas recebidas
    inicio_date = to_date(inicio)
    fim_date = to_date(fim)

    # Regras dos filtros
    if filtro == "mes":
        inicio_date = hoje - timedelta(days=30)
        fim_date = hoje

    elif filtro == "semana":
        inicio_date = hoje - timedelta(days=7)
        fim_date = hoje

    elif filtro == "periodo":
        if not inicio_date or not fim_date:
            # Se usuário não enviou datas, usa último mês
            inicio_date = hoje - timedelta(days=30)
            fim_date = hoje
    else:
        inicio_date = hoje - timedelta(days=30)
        fim_date = hoje

    # Buscar dados agrupados por dia
    dados = vendas_por_dia(empresa, inicio_date, fim_date)

    # Agora SIM calcular o total do período
    total_periodo = sum(d["total"] for d in dados)

    # Labels e valores para o gráfico
    labels = [d["dia"].strftime("%d/%m") for d in dados]
    valores = [float(d["total"]) for d in dados]

    # Gerar gráfico SVG inline
    grafico_svg = gerar_grafico_svg(labels, valores)

    # Totais por forma de pagamento
    totais_pagamento = (
        Venda.objects
        .filter(
            empresa=empresa,
            data__date__range=(inicio_date, fim_date),
            cancelada=False
        )
        .values("forma_pagamento")
        .annotate(
            total=Sum("total"),
            quantidade=Count("id")
        )
    )

    formas_dict = dict(Venda.FORMAS_PAGAMENTO)

    totais_pagamento_formatado = []
    labels_pagamento = []
    valores_pagamento = []

    total_pagamentos_geral = sum(item["total"] or 0 for item in totais_pagamento)

    for item in totais_pagamento:
        total = item["total"] or 0
        percentual = (total / total_pagamentos_geral * 100) if total_pagamentos_geral else 0

        forma_nome = formas_dict.get(item["forma_pagamento"])

        totais_pagamento_formatado.append({
            "forma": forma_nome,
            "total": total,
            "quantidade": item["quantidade"],
            "percentual": round(percentual, 2),
        })

        labels_pagamento.append(forma_nome)
        valores_pagamento.append(float(total))

    # Gerar gráfico pizza SVG
    grafico_pagamento_svg = gerar_grafico_svg(labels_pagamento, valores_pagamento)

    return render(request, "venda/relatorio_impressao.html", {
        "dados": dados,
        "grafico_svg": grafico_svg,
        "total_periodo": total_periodo,
        "totais_pagamento": totais_pagamento_formatado,
        "grafico_pagamento_svg": grafico_pagamento_svg,
        "inicio": inicio_date,
        "fim": fim_date,
    })






