import json
from decimal import Decimal

from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Produto, Empresa


class LoginView(auth_views.LoginView):
    template_name = "core/login.html"


class LogoutView(auth_views.LogoutView):
    pass


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

    return JsonResponse({"importados": contador})
