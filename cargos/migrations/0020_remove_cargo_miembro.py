# Generated by Django 2.2.6 on 2019-11-11 00:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0019_auto_20191111_0036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cargo',
            name='miembro',
        ),
    ]