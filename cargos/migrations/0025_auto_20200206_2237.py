# Generated by Django 2.2.6 on 2020-02-06 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0024_auto_20200205_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cargo',
            name='content_type',
        ),
        migrations.AddField(
            model_name='cargo',
            name='nivel',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cargos.Nivel'),
            preserve_default=False,
        ),
    ]
