# Generated by Django 2.2.14 on 2021-04-06 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0036_asignable_por_RER_y_REZ'),
    ]

    operations = [
        migrations.AddField(
            model_name='rango',
            name='asignable_RER',
            field=models.BooleanField(default=False, verbose_name='asignable por RER'),
        ),
    ]