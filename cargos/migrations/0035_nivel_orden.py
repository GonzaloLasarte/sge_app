# Generated by Django 2.2.14 on 2020-10-16 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0034_departamento_orden'),
    ]

    operations = [
        migrations.AddField(
            model_name='nivel',
            name='orden',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
