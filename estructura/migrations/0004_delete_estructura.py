# Generated by Django 2.2.6 on 2019-12-06 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0015_auto_20191206_1659'),
        ('estructura', '0003_auto_20191124_2326'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Estructura',
        ),
    ]
