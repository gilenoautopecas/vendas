import os
import django
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from django.conf import settings


# conectar ao django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vendas.settings")
django.setup()

from venda.models import Venda

TOKEN = "8325809654:AAGUsksqZMTOt1txd5eVdrfqdcktJSh_5BY"
TELEGRAM_CHAT_ID = ["1914515676", "7143573328"]


def formatar_real(valor):
    if valor is None:
        valor = Decimal("0.00")
    valor = Decimal(valor)
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot conectado ao sistema\n\n"
        "📋 Comandos disponíveis:\n\n"
        "/vendas_hoje\n"
        "/total_30_dias\n"
        "/ultimas_vendas\n"
        "/pagamentos hoje\n"
        "/pagamentos semana\n"
        "/pagamentos 30\n"
        "/caixa hoje\n"
        "/caixa semana\n"
        "/caixa 30\n"
        "/ranking_pagamentos hoje\n"
        "/ranking_pagamentos semana\n"
        "/ranking_pagamentos 30\n"
        "/venda 123\n"
    )


@sync_to_async
def buscar_total_30_dias():
    data_inicio = timezone.now() - timedelta(days=30)

    total = Venda.objects.filter(
        cancelada=False,
        data__gte=data_inicio
    ).aggregate(
        total=Sum("total")
    )["total"]

    return total or Decimal("0.00")


async def total_vendas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = await buscar_total_30_dias()

    await update.message.reply_text(
        f"💰 Total vendido nos últimos 30 dias:\n\n{formatar_real(total)}"
    )


@sync_to_async
def buscar_vendas_hoje():
    hoje = timezone.now().date()

    vendas = Venda.objects.filter(
        data__date=hoje,
        cancelada=False
    )

    qtd = vendas.count()

    total = vendas.aggregate(
        total=Sum("total")
    )["total"] or Decimal("0.00")

    return qtd, total


async def vendas_hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qtd, total = await buscar_vendas_hoje()

    await update.message.reply_text(
        f"📊 Vendas hoje\n\n"
        f"Quantidade: {qtd}\n"
        f"Total: {formatar_real(total)}"
    )


@sync_to_async
def buscar_ultimas_vendas():
    vendas = Venda.objects.filter(
        cancelada=False
    ).order_by("-id")[:5]

    return [(v.id, v.total or Decimal("0.00"), v.forma_pagamento) for v in vendas]


async def ultimas_vendas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vendas = await buscar_ultimas_vendas()

    texto = "🧾 Últimas vendas\n\n"

    if not vendas:
        texto += "Nenhuma venda encontrada."
    else:
        for venda_id, total, forma in vendas:
            texto += f"Venda #{venda_id} - {formatar_real(total)} - {forma}\n"

    await update.message.reply_text(texto)


@sync_to_async
def buscar_pagamentos(periodo):
    hoje = timezone.now()

    if periodo == "hoje":
        vendas = Venda.objects.filter(
            data__date=hoje.date(),
            cancelada=False
        )
    elif periodo == "semana":
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        vendas = Venda.objects.filter(
            data__date__gte=inicio_semana.date(),
            cancelada=False
        )
    elif periodo == "30":
        inicio = hoje - timedelta(days=30)
        vendas = Venda.objects.filter(
            data__gte=inicio,
            cancelada=False
        )
    else:
        vendas = Venda.objects.filter(cancelada=False)

    dados = vendas.values("forma_pagamento").annotate(
        total=Sum("total")
    )

    resultado = {
        "PIX": Decimal("0.00"),
        "CARTAO": Decimal("0.00"),
        "DINHEIRO": Decimal("0.00"),
        "NOTA": Decimal("0.00"),
    }

    for d in dados:
        resultado[d["forma_pagamento"]] = d["total"] or Decimal("0.00")

    return resultado


async def pagamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    periodo = "hoje"

    if context.args:
        periodo = context.args[0].lower()

    dados = await buscar_pagamentos(periodo)

    if periodo == "hoje":
        texto = "💳 Pagamentos de hoje\n\n"
    elif periodo == "semana":
        texto = "💳 Pagamentos da semana\n\n"
    elif periodo == "30":
        texto = "💳 Pagamentos dos últimos 30 dias\n\n"
    else:
        texto = "💳 Pagamentos\n\n"

    texto += (
        f"PIX: {formatar_real(dados['PIX'])}\n"
        f"Cartão: {formatar_real(dados['CARTAO'])}\n"
        f"Dinheiro: {formatar_real(dados['DINHEIRO'])}\n"
        f"Notinha: {formatar_real(dados['NOTA'])}"
    )

    await update.message.reply_text(texto)


@sync_to_async
def buscar_caixa(periodo):
    hoje = timezone.now()

    if periodo == "hoje":
        vendas = Venda.objects.filter(
            data__date=hoje.date(),
            cancelada=False
        )
    elif periodo == "semana":
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        vendas = Venda.objects.filter(
            data__date__gte=inicio_semana.date(),
            cancelada=False
        )
    elif periodo == "30":
        inicio = hoje - timedelta(days=30)
        vendas = Venda.objects.filter(
            data__gte=inicio,
            cancelada=False
        )
    else:
        vendas = Venda.objects.filter(cancelada=False)

    total = vendas.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    quantidade = vendas.count()

    ticket_medio = Decimal("0.00")
    if quantidade > 0:
        ticket_medio = total / quantidade

    pagamentos = vendas.values("forma_pagamento").annotate(
        total=Sum("total")
    )

    dados_pagamento = {
        "PIX": Decimal("0.00"),
        "CARTAO": Decimal("0.00"),
        "DINHEIRO": Decimal("0.00"),
        "NOTA": Decimal("0.00"),
    }

    for p in pagamentos:
        dados_pagamento[p["forma_pagamento"]] = p["total"] or Decimal("0.00")

    return total, quantidade, ticket_medio, dados_pagamento


async def caixa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    periodo = "hoje"

    if context.args:
        periodo = context.args[0].lower()

    total, qtd, ticket, pagamentos = await buscar_caixa(periodo)

    if periodo == "hoje":
        titulo = "📊 Caixa de hoje"
    elif periodo == "semana":
        titulo = "📊 Caixa da semana"
    elif periodo == "30":
        titulo = "📊 Caixa dos últimos 30 dias"
    else:
        titulo = "📊 Caixa"

    texto = (
        f"{titulo}\n\n"
        f"💰 Total: {formatar_real(total)}\n"
        f"🧾 Vendas: {qtd}\n"
        f"📈 Ticket médio: {formatar_real(ticket)}\n\n"
        f"💳 Pagamentos\n"
        f"PIX: {formatar_real(pagamentos['PIX'])}\n"
        f"Cartão: {formatar_real(pagamentos['CARTAO'])}\n"
        f"Dinheiro: {formatar_real(pagamentos['DINHEIRO'])}\n"
        f"Notinha: {formatar_real(pagamentos['NOTA'])}"
    )

    await update.message.reply_text(texto)


@sync_to_async
def buscar_ranking_pagamentos(periodo):
    hoje = timezone.now()

    if periodo == "hoje":
        vendas = Venda.objects.filter(data__date=hoje.date(), cancelada=False)
        titulo = "🏆 Ranking de pagamentos de hoje"
    elif periodo == "semana":
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        vendas = Venda.objects.filter(data__date__gte=inicio_semana.date(), cancelada=False)
        titulo = "🏆 Ranking de pagamentos da semana"
    else:
        inicio = hoje - timedelta(days=30)
        vendas = Venda.objects.filter(data__gte=inicio, cancelada=False)
        titulo = "🏆 Ranking de pagamentos dos últimos 30 dias"

    total_geral = vendas.aggregate(total=Sum("total"))["total"] or Decimal("0.00")

    pagamentos = list(
        vendas.values("forma_pagamento")
        .annotate(total=Sum("total"))
        .order_by("-total")
    )

    resultado = []
    for item in pagamentos:
        total = item["total"] or Decimal("0.00")
        percentual = (total / total_geral * 100) if total_geral > 0 else Decimal("0.00")
        resultado.append({
            "forma": item["forma_pagamento"],
            "total": total,
            "percentual": percentual,
        })

    return titulo, total_geral, resultado


async def ranking_pagamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    periodo = "hoje"

    if context.args:
        periodo = context.args[0].lower()

    if periodo not in ["hoje", "semana", "30"]:
        periodo = "hoje"

    titulo, total_geral, ranking = await buscar_ranking_pagamentos(periodo)

    texto = f"{titulo}\n\nTotal geral: {formatar_real(total_geral)}\n\n"

    if not ranking:
        texto += "Nenhuma venda encontrada."
    else:
        nomes = {
            "PIX": "PIX",
            "CARTAO": "Cartão",
            "DINHEIRO": "Dinheiro",
            "NOTA": "Notinha",
        }

        for i, item in enumerate(ranking, start=1):
            nome = nomes.get(item["forma"], item["forma"])
            texto += (
                f"{i}. {nome}: {formatar_real(item['total'])} "
                f"({item['percentual']:.1f}%)\n"
            )

    await update.message.reply_text(texto)


@sync_to_async
def buscar_venda_por_id(venda_id):
    try:
        venda = (
            Venda.objects
            .prefetch_related("itens__produto")
            .get(id=venda_id)
        )
    except Venda.DoesNotExist:
        return None

    itens = []
    for item in venda.itens.all():
        itens.append({
            "produto": item.produto.nome,
            "quantidade": item.quantidade,
            "subtotal": item.subtotal,
            "preco_unitario": item.preco_unitario,
        })

    return {
        "id": venda.id,
        "data": venda.data,
        "total": venda.total,
        "forma_pagamento": venda.get_forma_pagamento_display(),
        "cancelada": venda.cancelada,
        "observacao": venda.observacao,
        "itens": itens,
    }


async def venda_numero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim: /venda 123")
        return

    try:
        venda_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Informe um número válido. Exemplo: /venda 123")
        return

    venda = await buscar_venda_por_id(venda_id)

    if not venda:
        await update.message.reply_text(f"Venda #{venda_id} não encontrada.")
        return

    texto = (
        f"🧾 Venda #{venda['id']}\n\n"
        f"📅 Data: {venda['data'].strftime('%d/%m/%Y %H:%M')}\n"
        f"💰 Total: {formatar_real(venda['total'])}\n"
        f"💳 Pagamento: {venda['forma_pagamento']}\n"
        f"❌ Cancelada: {'Sim' if venda['cancelada'] else 'Não'}\n"
    )

    if venda["observacao"]:
        texto += f"📝 Obs: {venda['observacao']}\n"

    if venda["itens"]:
        texto += "\nItens:\n"
        for item in venda["itens"]:
            texto += (
                f"- {item['produto']} | "
                f"Qtd: {item['quantidade']} | "
                f"Unit.: {formatar_real(item['preco_unitario'])} | "
                f"Subtotal: {formatar_real(item['subtotal'])}\n"
            )

    await update.message.reply_text(texto)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("total_30_dias", total_vendas))
app.add_handler(CommandHandler("vendas_hoje", vendas_hoje))
app.add_handler(CommandHandler("ultimas_vendas", ultimas_vendas))
app.add_handler(CommandHandler("pagamentos", pagamentos))
app.add_handler(CommandHandler("caixa", caixa))
app.add_handler(CommandHandler("ranking_pagamentos", ranking_pagamentos))
app.add_handler(CommandHandler("venda", venda_numero))

app.run_polling()
