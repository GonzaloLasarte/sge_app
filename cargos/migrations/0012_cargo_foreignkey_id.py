# Generated by Django 2.2.6 on 2019-11-10 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0011_auto_20191110_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='foreignkey_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
