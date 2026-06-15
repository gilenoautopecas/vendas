from django.urls import path
from .views import criar_produto_ajax

urlpatterns = [
    path("criar-produto-ajax/", criar_produto_ajax, name="criar_produto_ajax"),
]
