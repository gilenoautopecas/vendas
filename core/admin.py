from django.contrib import admin
from .models import Produto
# Register your models here.

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    model = Produto
