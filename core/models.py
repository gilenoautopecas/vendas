import secrets

from django.conf import settings
from django.db import models


class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    sync_token = models.CharField(max_length=64, unique=True, editable=False)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    ultima_sincronizacao = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sync_token:
            self.sync_token = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    def __str__(self):
        return f"{self.user.username} - {self.empresa.nome}"


class Produto(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="produtos"
    )
    codigo_gdoor = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    nome = models.CharField(max_length=150)
    preco_padrao = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "codigo_gdoor"],
                name="unique_codigo_gdoor_por_empresa"
            )
        ]

    def __str__(self):
        return self.nome
