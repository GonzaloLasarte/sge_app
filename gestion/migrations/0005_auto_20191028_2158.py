# Generated by Django 2.2.6 on 2019-10-28 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0004_auto_20191027_1806'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extendeduser',
            options={'verbose_name': 'ususario', 'verbose_name_plural': 'usuarios'},
        ),
        migrations.AddField(
            model_name='miembrocargo',
            name='fecha_baja',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='miembrocargo',
            name='fecha_inicio',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='admission_date',
            field=models.DateField(blank=True, null=True, verbose_name='fecha de ingreso'),
        ),
    ]
