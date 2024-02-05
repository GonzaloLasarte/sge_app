# Generated by Django 2.2.6 on 2019-10-27 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0003_auto_20191027_1752'),
        ('estructura', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='estructura',
            name='miembro',
            field=models.ManyToManyField(through='gestion.MiembroGrupo', to='gestion.Member'),
        ),
        migrations.AddField(
            model_name='grupo',
            name='miembros',
            field=models.ManyToManyField(through='gestion.MiembroGrupo', to='gestion.Member'),
        ),
    ]