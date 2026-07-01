import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("venda", "0005_venda_empresa_padrao"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venda",
            name="empresa",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="vendas",
                to="core.empresa",
            ),
        ),
    ]
