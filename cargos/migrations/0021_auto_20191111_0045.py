# Generated by Django 2.2.6 on 2019-11-11 00:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cargos', '0020_remove_cargo_miembro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cargo',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
