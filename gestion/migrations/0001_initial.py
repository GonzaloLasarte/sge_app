# Generated by Django 2.2.6 on 2019-10-27 17:17

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import gestion.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estudio', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nombre')),
                ('sirname', models.CharField(max_length=255, verbose_name='apellidos')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='fecha de nacimiento')),
                ('admission_date', models.DateField(blank=True, null=True, verbose_name='fecha de ingreso')),
                ('dni', models.CharField(blank=True, max_length=10, null=True, verbose_name='DNI')),
                ('address', models.CharField(blank=True, max_length=500, null=True, verbose_name='dirección')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='población')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='provincia')),
                ('postal_code', models.IntegerField(blank=True, null=True, verbose_name='código postal')),
                ('phone', models.IntegerField(blank=True, null=True, verbose_name='teléfono')),
                ('cellphone', models.IntegerField(blank=True, null=True, verbose_name='móvil')),
                ('email', models.EmailField(blank=True, max_length=200, null=True, verbose_name='e-mail')),
                ('gender', models.CharField(choices=[('H', 'Hombre'), ('M', 'Mujer')], max_length=10, verbose_name='género')),
                ('charge', models.CharField(blank=True, choices=[('R', 'Resp. Titular'), ('V-', 'Vice. Titular'), ('H', 'Resp. DH'), ('V-H', 'Vice-Resp. DH'), ('M', 'Resp. DM'), ('V-M', 'Vice-Resp. DM'), ('HJ', 'Resp. DHJ'), ('V-HJ', 'Vice-Resp. DHJ'), ('MJ', 'Resp. DMJ'), ('V-MJ', 'Vice-Resp. DMJ')], max_length=20, null=True, verbose_name='cargo')),
                ('in_charge_of', models.CharField(blank=True, choices=[('G', 'GRUPO'), ('D', 'DISTRITO'), ('DG', 'DIST. GRAL'), ('Z', 'ZONA'), ('R', 'REGION'), ('N', 'NACIONAL')], max_length=20, null=True, verbose_name='a cargo de')),
                ('study', models.CharField(blank=True, choices=[('Grado 1', 'Grado 1'), ('Grado 2', 'Grado 2'), ('Grado 3', 'Grado 3'), ('Grado 4', 'Grado 4')], max_length=7, null=True, verbose_name='estudio')),
                ('others', models.CharField(blank=True, max_length=100, null=True, verbose_name='otros')),
                ('subscription', models.BooleanField(default=0, verbose_name='suscripción')),
                ('omamori_gohonzon', models.BooleanField(default=0)),
                ('register', models.CharField(blank=True, choices=[('Ingreso con entrega de Gohonzon', 'Ingreso con entrega de Gohonzon'), ('Ingreso sin entrega de Gohonzon', 'Ingreso sin entrega de Gohonzon'), ('Llegada desde el extranjero', 'Llegada desde el extranjero')], max_length=50, null=True, verbose_name='alta')),
                ('origin', models.CharField(blank=True, max_length=50, null=True, verbose_name='procedencia')),
                ('drop_out', models.CharField(blank=True, choices=[('Por solicitud', 'Por solicitud'), ('Por traslado a otro país', 'Por traslado a otro país'), ('Por fallecimiento', 'Por fallecimiento')], max_length=50, null=True, verbose_name='baja')),
                ('destination', models.CharField(blank=True, max_length=50, null=True, verbose_name='destino')),
                ('photo', models.ImageField(blank=True, upload_to=gestion.models.user_directory_path, verbose_name='foto')),
                ('recommended_by', models.ManyToManyField(blank=True, related_name='_member_recommended_by_+', to='gestion.Member', verbose_name='recomendado por')),
            ],
            options={
                'verbose_name': 'member',
                'verbose_name_plural': 'members',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('caducidad', models.DateField(default=datetime.datetime(2019, 6, 27, 17, 17, 8, 82617))),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('miembro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.Member')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'información de usario',
                'verbose_name_plural': 'información de usuarios',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
