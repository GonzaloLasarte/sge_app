# Generated by Django 2.2.6 on 2019-11-23 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0011_delete_miembrocargo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extendeduser',
            options={'verbose_name': 'usuario', 'verbose_name_plural': 'usuarios'},
        ),
        migrations.AddField(
            model_name='member',
            name='recomendacion',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='recomendación'),
        ),
    ]