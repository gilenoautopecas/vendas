from django.contrib import admin
from .models import Produto, Empresa, PerfilUsuario


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    model = Produto
    list_display = ("nome", "empresa", "codigo_gdoor", "preco_padrao", "ativo")
    list_filter = ("empresa", "ativo")
    ordering = ("-codigo_gdoor",)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ativa", "sync_token", "criado_em")
    prepopulated_fields = {"slug": ("nome",)}
    readonly_fields = ("sync_token",)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "empresa")
    list_filter = ("empresa",)
