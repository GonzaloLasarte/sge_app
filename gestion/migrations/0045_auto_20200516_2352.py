# Generated by Django 2.2.6 on 2020-05-16 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0044_auto_20200506_2237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='observaciones',
            new_name='observaciones_al_estudio',
        ),
    ]