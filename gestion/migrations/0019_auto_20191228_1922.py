# Generated by Django 2.2.6 on 2019-12-28 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0018_auto_20191228_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='gohonzon',
            field=models.DateField(blank=True, null=True),
        ),
    ]
