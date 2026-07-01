from django.db import models
from core.models import *

# Create your models here.
class Venda(models.Model):
    DINHEIRO = "DINHEIRO"
    PIX = "PIX"
    CARTAO = "CARTAO"
    NOTA = "NOTA"

    FORMAS_PAGAMENTO = [
        (DINHEIRO, "Dinheiro"),
        (PIX, "PIX"),
        (CARTAO, "Cartão"),
        (NOTA, "Notinha"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="vendas"
    )
    data = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=30, choices=FORMAS_PAGAMENTO)
    observacao = models.TextField(blank=True, null=True)
    cancelada = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)

    def __str__(self):
        return f"Venda {self.id} - {self.data}"



class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name="itens", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
