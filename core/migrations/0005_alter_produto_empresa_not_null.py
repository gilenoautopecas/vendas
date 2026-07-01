import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_empresa_padrao"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="empresa",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="produtos",
                to="core.empresa",
            ),
        ),
    ]
