# Generated by Django 2.2.6 on 2020-04-18 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0030_cargocapacitacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='RangoCapacitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('fecha_inicio', models.DateField(auto_now_add=True)),
                ('fecha_baja', models.DateField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'rango de capacitación',
                'verbose_name_plural': 'rangos de capacitación',
                'ordering': ['nombre'],
            },
        ),
        migrations.AlterModelOptions(
            name='cargo',
            options={'verbose_name': 'cargo de responsabilidad', 'verbose_name_plural': 'cargos de responsabilidad'},
        ),
        migrations.AlterModelOptions(
            name='rango',
            options={'ordering': ['nombre'], 'verbose_name': 'rango de responsabilidad', 'verbose_name_plural': 'rangos de responsabilidad'},
        ),
        migrations.AlterField(
            model_name='cargocapacitacion',
            name='rango',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cargos.RangoCapacitacion'),
        ),
    ]
