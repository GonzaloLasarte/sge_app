# Generated by Django 2.2.14 on 2021-05-03 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0037_rango_asignable_rer'),
    ]

    operations = [
        migrations.AddField(
            model_name='rangocapacitacion',
            name='asignable_RER',
            field=models.BooleanField(default=False, verbose_name='asignable por RER'),
        ),
    ]
