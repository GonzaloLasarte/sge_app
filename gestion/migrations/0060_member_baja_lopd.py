# Generated by Django 2.2.14 on 2021-05-17 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0059_motivos_altas_y_bajas'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='baja_lopd',
            field=models.BooleanField(default=False, verbose_name='Baja por LOPD'),
        ),
    ]