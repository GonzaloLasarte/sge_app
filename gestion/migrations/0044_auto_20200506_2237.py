# Generated by Django 2.2.6 on 2020-05-06 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0043_auto_20200506_2228'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='member',
            name='gestion_mem_nombre_68d407_idx',
        ),
        migrations.AlterField(
            model_name='member',
            name='apellidos',
            field=models.CharField(max_length=255, verbose_name='apellidos'),
        ),
        migrations.AlterField(
            model_name='member',
            name='email',
            field=models.EmailField(blank=True, max_length=200, null=True, verbose_name='e-mail'),
        ),
        migrations.AlterField(
            model_name='member',
            name='fecha_ingreso',
            field=models.DateField(blank=True, null=True, verbose_name='fecha de ingreso'),
        ),
        migrations.AlterField(
            model_name='member',
            name='movil',
            field=models.IntegerField(blank=True, null=True, verbose_name='móvil'),
        ),
        migrations.AlterField(
            model_name='member',
            name='nombre',
            field=models.CharField(max_length=255, verbose_name='nombre'),
        ),
    ]
