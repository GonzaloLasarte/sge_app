# Generated by Django 2.2.6 on 2020-03-15 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estructura', '0006_auto_20200213_2106'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='region',
            index=models.Index(fields=['nombre'], name='estructura__nombre_caa490_idx'),
        ),
    ]
