from django.contrib import admin
from .models import Venda, ItemVenda
# Register your models here.

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'total') # Campos para exibir