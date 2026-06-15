from django.db import models

# Create your models here.

class Produto(models.Model):
    codigo_gdoor = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    nome = models.CharField(max_length=150)
    preco_padrao = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

