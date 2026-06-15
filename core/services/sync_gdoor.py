from decimal import Decimal

from core.models import Produto
from core.services.gdoor import buscar_produtos_gdoor


def sincronizar_produtos():
    produtos = buscar_produtos_gdoor()

    contador = 0

    for p in produtos:
        try:
            preco = Decimal(str(p.get("preco_venda", 0) or 0))
        except Exception:
            preco = Decimal("0.00")

        try:
            Produto.objects.update_or_create(
                codigo_gdoor=p["codigo"],
                defaults={
                    "nome": p.get("descricao", "")[:150],
                    "preco_padrao": preco,
                    "ativo": True,
                }
            )

            contador += 1

        except Exception as e:
            print(
                f"Erro ao importar produto "
                f"{p.get('codigo')} - {p.get('descricao')}: {e}"
            )

    return contador
