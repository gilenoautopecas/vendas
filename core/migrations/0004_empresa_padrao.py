import secrets

from django.db import migrations


def criar_empresa_padrao_e_associar(apps, schema_editor):
    Empresa = apps.get_model("core", "Empresa")
    Produto = apps.get_model("core", "Produto")

    if not Produto.objects.filter(empresa__isnull=True).exists():
        return

    empresa, _ = Empresa.objects.get_or_create(
        slug="padrao",
        defaults={
            "nome": "Empresa Padrão",
            "ativa": True,
            "sync_token": secrets.token_hex(32),
        }
    )

    Produto.objects.filter(empresa__isnull=True).update(empresa=empresa)


def reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_empresa_perfilusuario_alter_produto_codigo_gdoor_and_more"),
    ]

    operations = [
        migrations.RunPython(criar_empresa_padrao_e_associar, reverter),
    ]
