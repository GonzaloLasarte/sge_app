# Generated by Django 2.2.6 on 2020-03-15 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estructura', '0010_historicoestructura_anterior_fk'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicoestructura',
            old_name='anterior_fk',
            new_name='fk',
        ),
    ]
