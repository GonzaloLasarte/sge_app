# Generated by Django 2.2.6 on 2020-03-15 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estructura', '0009_historicoestructura_fecha_baja'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicoestructura',
            name='anterior_fk',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]