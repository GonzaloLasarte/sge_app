# Generated by Django 2.2.6 on 2020-03-15 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0032_auto_20200303_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='miembrogrupocapacitacion',
            name='fecha_baja',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
    ]