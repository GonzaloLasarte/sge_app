# Generated by Django 2.2.14 on 2021-05-17 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0060_member_baja_lopd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='apellidos',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='apellidos'),
        ),
        migrations.AlterField(
            model_name='member',
            name='nombre',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='nombre'),
        ),
    ]