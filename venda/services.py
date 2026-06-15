from decimal import Decimal
from .models import Venda, ItemVenda

from django.db.models import Sum


def atualizar_total_venda(venda):
    total = venda.itens.aggregate(
        total=Sum("subtotal")
    )["total"] or Decimal("0.00")

    venda.total = total
    venda.save(update_fields=["total"])



def criar_venda(forma_pagamento, observacao=None):
    venda = Venda.objects.create(
        forma_pagamento=forma_pagamento,
        observacao=observacao or ""
    )
    return venda


def adicionar_item(venda, produto, quantidade, preco_unitario=None):
    if preco_unitario is None:
        preco_unitario = produto.preco_padrao

    subtotal = Decimal(quantidade) * Decimal(preco_unitario)

    item = ItemVenda.objects.create(
        venda=venda,
        produto=produto,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        subtotal=subtotal
    )

    atualizar_total_venda(venda)

    return item


def remover_item(item):
    venda = item.venda
    item.delete()
    atualizar_total_venda(venda)


def cancelar_venda(venda):
    venda.cancelada = True
    venda.save(update_fields=["cancelada"])


def calcular_total_venda(venda):
    total = sum(item.subtotal for item in venda.itens.all())
    venda.total = total
    venda.save()


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import StringIO
import base64

def gerar_grafico_svg(labels, valores):
    fig, ax = plt.subplots(figsize=(8, 3))  # tamanho ideal para impressão

    ax.bar(labels, valores, color="#3b82f6")
    ax.set_title("Vendas por Dia")
    ax.set_xlabel("Dia")
    ax.set_ylabel("Total (R$)")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Salvar em SVG em memória
    img_data = StringIO()
    fig.savefig(img_data, format="svg", bbox_inches="tight")
    plt.close(fig)

    return img_data.getvalue()
