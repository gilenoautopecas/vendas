from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("visualizar/<int:venda_id>/", views.visualizar_venda, name="visualizar_venda"),
    path("finalizar/<int:venda_id>/", views.finalizar_venda_view, name="finalizar_venda"),
    path("cancelar/<int:venda_id>/", views.cancelar_venda_view, name="cancelar_venda"),
    path("excluir/<int:venda_id>/", views.excluir_venda, name="excluir_venda"),
    path("nova/", views.nova_venda, name="nova_venda"),
    path("editar/<int:venda_id>/", views.editar_venda, name="editar_venda"),
    path("deletar-item/<int:item_id>/", views.deletar_item, name="deletar_item"),
    path("pdf/<int:venda_id>/", views.imprimir_venda_pdf, name="imprimir_venda_pdf"),
    path("relatorios/", views.relatorios, name="relatorios"),
    path("relatorios/imprimir/", views.imprimir_relatorio, name="imprimir_relatorio"),
    path("produtos/", views.produtos, name="produtos"),

    path(
        "importar-produtos-gdoor/",
        views.importar_produtos_gdoor,
        name="importar_produtos_gdoor"
    ),

]
