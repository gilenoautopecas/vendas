import secrets

from django.db import migrations


def associar_empresa_padrao(apps, schema_editor):
    Empresa = apps.get_model("core", "Empresa")
    Venda = apps.get_model("venda", "Venda")

    if not Venda.objects.filter(empresa__isnull=True).exists():
        return

    empresa, _ = Empresa.objects.get_or_create(
        slug="padrao",
        defaults={
            "nome": "Empresa Padrão",
            "ativa": True,
            "sync_token": secrets.token_hex(32),
        }
    )

    Venda.objects.filter(empresa__isnull=True).update(empresa=empresa)


def reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("venda", "0004_venda_empresa"),
        ("core", "0004_empresa_padrao"),
    ]

    operations = [
        migrations.RunPython(associar_empresa_padrao, reverter),
    ]
