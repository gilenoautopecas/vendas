import json
import re
from decimal import Decimal

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Produto, Empresa, PerfilUsuario


class LoginView(auth_views.LoginView):
    template_name = "core/login.html"


class LogoutView(auth_views.LogoutView):
    pass


@login_required
def setup_empresa(request):
    # Já tem empresa — vai pro dashboard
    try:
        request.user.perfil
        return redirect("dashboard")
    except Exception:
        pass

    erro = None

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()

        if not nome:
            erro = "O nome da empresa é obrigatório."
        else:
            # Gera slug a partir do nome
            slug = re.sub(r"[^a-z0-9]+", "-", nome.lower()).strip("-")
            # Garante unicidade do slug
            base_slug, contador = slug, 1
            while Empresa.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1

            empresa = Empresa.objects.create(nome=nome, slug=slug)
            PerfilUsuario.objects.create(user=request.user, empresa=empresa)
            return redirect("dashboard")

    return render(request, "core/setup_empresa.html", {"erro": erro})


@require_POST
def criar_produto_ajax(request):
    nome = request.POST.get("nome")
    preco = request.POST.get("preco")

    if not nome or not preco:
        return JsonResponse({"erro": "Dados inválidos"}, status=400)

    produto = Produto.objects.create(
        empresa=request.user.perfil.empresa,
        nome=nome,
        preco_padrao=preco
    )

    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome,
        "preco": str(produto.preco_padrao)
    })


@csrf_exempt
@require_POST
def sync_produtos(request):
    token = request.headers.get("Authorization", "").removeprefix("Token ").strip()

    if not token:
        return JsonResponse({"erro": "Token não informado"}, status=401)

    try:
        empresa = Empresa.objects.get(sync_token=token, ativa=True)
    except Empresa.DoesNotExist:
        return JsonResponse({"erro": "Token inválido"}, status=401)

    try:
        payload = json.loads(request.body)
        produtos = payload.get("produtos", [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"erro": "Payload inválido"}, status=400)

    contador = 0

    for p in produtos:
        try:
            preco = Decimal(str(p.get("preco_venda", 0) or 0))
        except Exception:
            preco = Decimal("0.00")

        codigo = p.get("codigo")
        if not codigo:
            continue

        try:
            Produto.objects.update_or_create(
                empresa=empresa,
                codigo_gdoor=codigo,
                defaults={
                    "nome": (p.get("descricao") or "")[:150],
                    "preco_padrao": preco,
                    "ativo": True,
                }
            )
            contador += 1
        except Exception:
            continue

    empresa.ultima_sincronizacao = timezone.now()
    empresa.save(update_fields=["ultima_sincronizacao"])

    return JsonResponse({"importados": contador})
