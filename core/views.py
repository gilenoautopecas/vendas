from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Produto


@require_POST
def criar_produto_ajax(request):
    nome = request.POST.get("nome")
    preco = request.POST.get("preco")

    if not nome or not preco:
        return JsonResponse({"erro": "Dados inválidos"}, status=400)

    produto = Produto.objects.create(
        nome=nome,
        preco_padrao=preco
    )

    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome,
        "preco": str(produto.preco_padrao)
    })
