# Generated by Django 2.2.6 on 2019-11-10 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0013_auto_20191110_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='object_id',
            field=models.PositiveIntegerField(),
        ),
    ]
