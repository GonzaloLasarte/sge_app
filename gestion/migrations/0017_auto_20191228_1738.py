# Generated by Django 2.2.6 on 2019-12-28 17:38

from django.db import migrations, models
import gestion.models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0016_auto_20191208_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='genero',
        ),
        migrations.AlterField(
            model_name='member',
            name='carta',
            field=models.ImageField(blank=True, null=True, upload_to=gestion.models.user_directory_path, verbose_name='carta'),
        ),
        migrations.AlterField(
            model_name='member',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to=gestion.models.user_directory_path, verbose_name='foto'),
        ),
    ]