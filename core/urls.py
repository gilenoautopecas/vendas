from django.urls import path
from .views import criar_produto_ajax, sync_produtos

urlpatterns = [
    path("criar-produto-ajax/", criar_produto_ajax, name="criar_produto_ajax"),
    path("sync-produtos/", sync_produtos, name="sync_produtos"),
]
