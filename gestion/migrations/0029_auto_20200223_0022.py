# Generated by Django 2.2.6 on 2020-02-23 00:22

from django.db import migrations, models
import gestion.models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0028_auto_20200213_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='carta',
            field=models.FileField(blank=True, null=True, upload_to=gestion.models.user_directory_path, verbose_name='carta'),
        ),
    ]