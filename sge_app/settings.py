"""
Django settings for sge_app project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import socket

from django.utils.translation import gettext_lazy as _

import pymysql
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Always use IPython for shell_plus
SHELL_PLUS = "ipython"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "+!h1hnb93$qf%gwa4l2(ao*l@e1%oy$376z4f63(egb46!mgix"

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = "localhost"

# SECURITY WARNING: don't run with debug turned on in production!
if HOSTNAME == "ns1780.cloud-premium.com":
    DEBUG = False
else:
    DEBUG = True

if HOSTNAME == "pre.gestion-sokagakkai.org":
    PRE = True
else:
    PRE = False

ALLOWED_HOSTS = ["gestion-sokagakkai.org", "www.gestion-sokagakkai.org", "localhost", "pre.gestion-sokagakkai.org"]


# Application definition

INSTALLED_APPS = [
    "cargos.apps.CargosConfig",
    "estructura.apps.EstructuraConfig",
    "gestion.apps.GestionConfig",
    "accounts.apps.AccountsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "admin_reorder",
    "django_cleanup.apps.CleanupConfig",
    "django_extensions",
]

# GRAPH_MODELS = {
#   'all_applications': True,
#   'group_models': True,
# }

MIDDLEWARE = [
    "gestion.middleware.ExpiredUserMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "admin_reorder.middleware.ModelAdminReorder",
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = "sge_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sge_app.wsgi.application"

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "gestions_sge_db",
            "USER": "root",
            #"PASSWORD": "root",
            # 'NAME': 'sgeappDB',
            # 'USER': 'sgeappadmin',
            # 'PASSWORD': 'SuperUser2019.',
            "HOST": "localhost",
            "PORT": "3306",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "gestions_sge_db",
            "USER": "gestions_sgeuser",
            #"PASSWORD": "X@)XE-Gwf.m#PU",
            # 'HOST': 'shx35.guebs.net',
            "HOST": "localhost",
            "PORT": "3306",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "es"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_L10N = True

USE_TZ = True

from django.conf.locale.es import formats as es_formats

es_formats.DATE_FORMAT = "d/m/Y"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


if DEBUG:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")

elif PRE:
    STATIC_URL = "/"
    STATIC_ROOT = "/home/gestions/python/pre.gestion-sokagakkai.org/public/"
    
else :
    STATIC_URL = "/"
    STATIC_ROOT = "/home/gestions/python/sge_app/public/"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

LANGUAGES = (
    ("en", _("English")),
    ("es", _("Spanish")),
)

MEDIA_URL = "/media/"
if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "public", "media")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

ADMIN_REORDER = (
    # Reorder app models
    {"app": "gestion", "models": ("gestion.Member", "gestion.ExtendedUser", "gestion.MiembroCargo", "gestion.Estudio")},
    {
        "app": "estructura",
        "models": (
            "estructura.Region",
            "estructura.Zona",
            "estructura.DistritoGeneral",
            "estructura.Distrito",
            "estructura.Grupo",
        ),
    },
    {"app": "cargos", "label": "cargos común", "models": ("cargos.Departamento", "cargos.Nivel")},
    {"app": "cargos", "label": "cargos de responsabilidad", "models": ("cargos.Rango", "cargos.Cargo")},
    {
        "app": "cargos",
        "label": "cargos de capacitación",
        "models": ("cargos.RangoCapacitacion", "cargos.GrupoCapacitacion", "cargos.CargoCapacitacion"),
    },
    "auth",
)

AUTH_USER_MODEL = "gestion.ExtendedUser"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    }
}

if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "logfile": {
                "class": "logging.FileHandler",
                "filename": "log/server.log",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["logfile"],
            },
        },
    }

DEFAULT_FILE_STORAGE = "storages.backends.ftp.FTPStorage"
FTP_STORAGE_LOCATION = "ftp://media@gestion-sokagakkai.org:=ZPa$MXqjP@ftp.gestion-sokagakkai.org:21"
LOCATION = "ftp://media@gestion-sokagakkai.org:=ZPa$MXqjP@ftp.gestion-sokagakkai.org"

FTP_HOST = "ftp.gestion-sokagakkai.org"
FTP_USER = "media@gestion-sokagakkai.org"
FTP_PASSWORD = "=ZPa$MXqjP"

DB_WOOCOMMERCE_DATABASE = "edicion7_sgsfscwq20w"
DB_WOOCOMMERCE_USER = "edicion7_ab9342"
DB_WOOCOMMERCE_PASSWORD = "tZQb.WxK@@XF"
DB_WOOCOMMERCE_HOST = "localhost"

SESSION_EXPIRE_SECONDS = 60 * 30
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True