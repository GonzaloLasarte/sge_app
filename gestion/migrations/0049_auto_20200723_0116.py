# Generated by Django 2.2.14 on 2020-07-22 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0048_auto_20200601_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='descripcion',
            field=models.CharField(choices=[('Solicitud de Ingreso', 'Solicitud de Ingreso'), ('Propuesta de Nombramiento', 'Propuesta de Nombramiento'), ('Solicitud de Entrega de Omamori', 'Solicitud de Entrega de Omamori'), ('Gohonzon', 'Gohonzon'), ('Autorización a menores', 'Autorización a menores'), ('Carta de Presentación', 'Carta de Presentación'), ('Formulario de Visita a Centro Cultural', 'Formulario de Visita a Centro Cultural'), ('Solicitud de baja', 'Solicitud de baja'), ('Otros', 'Otros')], db_index=True, help_text='Descripción corta del archivo (max 50 caracteres)', max_length=50, verbose_name='descripcion'),
        ),
        migrations.AlterField(
            model_name='member',
            name='alta',
            field=models.CharField(blank=True, choices=[('Ingreso con entrega de Gohonzon', 'Ingreso con entrega de Gohonzon'), ('Ingreso sin entrega de Gohonzon', 'Ingreso sin entrega de Gohonzon'), ('Llegada desde el extranjero', 'Llegada desde el extranjero'), ('Siendo miembro recibe Gohonzon', 'Siendo miembro recibe Gohonzon')], max_length=50, null=True, verbose_name='alta'),
        ),
    ]
