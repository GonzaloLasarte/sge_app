# Generated by Django 2.2.6 on 2020-03-03 21:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0028_grupocapacitacion'),
        ('gestion', '0031_auto_20200223_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='dni',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='DNI/NIE/PASAPORTE'),
        ),
        migrations.CreateModel(
            name='MiembroGrupoCapacitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(auto_now_add=True, null=True)),
                ('fecha_baja', models.DateField(blank=True, null=True)),
                ('grupo_capacitacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cargos.GrupoCapacitacion', verbose_name='Grupo de capacitación')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.Member')),
            ],
            options={
                'verbose_name': 'pertenencia a grupo de capacitación',
                'verbose_name_plural': 'pertenencias a grupo de capacitación',
            },
        ),
        migrations.AddIndex(
            model_name='miembrogrupocapacitacion',
            index=models.Index(fields=['member'], name='gestion_mie_member__bcc5a8_idx'),
        ),
        migrations.AddIndex(
            model_name='miembrogrupocapacitacion',
            index=models.Index(fields=['member', 'grupo_capacitacion'], name='gestion_mie_member__10fd8b_idx'),
        ),
    ]
