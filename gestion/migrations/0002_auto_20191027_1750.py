# Generated by Django 2.2.6 on 2019-10-27 17:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extendeduser',
            name='caducidad',
            field=models.DateField(default=datetime.datetime(2019, 6, 27, 17, 50, 21, 657049)),
        ),
    ]
