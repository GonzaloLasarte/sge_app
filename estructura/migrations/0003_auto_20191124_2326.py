# Generated by Django 2.2.6 on 2019-11-24 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('estructura', '0002_auto_20191027_1752'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estructura',
            name='zona_general',
        ),
        migrations.RemoveField(
            model_name='zona',
            name='zona_general',
        ),
        migrations.AddField(
            model_name='zona',
            name='region',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='estructura.Region'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ZonaGeneral',
        ),
    ]