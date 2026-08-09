"""
Django settings for ecommerce project.
Generado por 'django-admin startproject' usando Django 5.2.8
"""

import os
from pathlib import Path

from corsheaders.defaults import default_headers, default_methods
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Variables de entorno
# =========================

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# =========================
# Aplicaciones
# =========================

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # Terceros
    'rest_framework',
    'corsheaders',
    'django_filters',

    # Apps del proyecto
    'apps.clientes.apps.ClientesConfig',
    'apps.adminpanel.apps.AdminpanelConfig',
    'apps.productos.apps.ProductosConfig',
    'apps.pedidos.apps.PedidosConfig',
    'apps.usuarios.apps.UsuariosConfig',
    'apps.analitica.apps.AnaliticaConfig',
    'apps.recomendacion.apps.RecomendacionConfig',
    'apps.reporting.apps.ReportingConfig',
]

AUTH_USER_MODEL = 'usuarios.Usuario'


# =========================
# Middleware
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================
# CORS
# =========================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

CORS_ALLOW_METHODS = list(default_methods)


# =========================
# CSRF
# =========================

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_HTTPONLY = False

# Importante para desarrollo con frontend separado
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False


# =========================
# URLs
# =========================

ROOT_URLCONF = 'ecommerce.urls'


# =========================
# Templates
# =========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]


WSGI_APPLICATION = 'ecommerce.wsgi.application'


# =========================
# Database
# =========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# Password validation
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]


# =========================
# Internacionalización
# =========================

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True


# =========================
# Static & Media
# =========================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# Default PK
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================
# Django Rest Framework
# =========================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],

    # =========================
    # PAGINACION GLOBAL
    # =========================
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,

    # =========================
    # FILTROS
    # =========================
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
    ],
}