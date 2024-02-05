# Generated by Django 2.2.6 on 2019-11-10 20:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0007_auto_20191110_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='fecha_inicio',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='departamento',
            name='fecha_baja',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='departamento',
            name='fecha_inicio',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nivel',
            name='fecha_baja',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nivel',
            name='fecha_inicio',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rango',
            name='fecha_baja',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rango',
            name='fecha_inicio',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
