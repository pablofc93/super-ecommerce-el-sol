
"""
Django settings for ecommerce project.
"""

import os
from pathlib import Path

from corsheaders.defaults import default_headers, default_methods
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Variables de entorno
# =========================

load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-local-development-only-change-me"
    else:
        raise ImproperlyConfigured(
            "Debes configurar SECRET_KEY en las variables de entorno."
        )

# Render proporciona RENDER_EXTERNAL_HOSTNAME automáticamente.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS", "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]

RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Eliminar posibles duplicados.
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))


# =========================
# Aplicaciones
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",

    "rest_framework",
    "corsheaders",
    "django_filters",

    "apps.clientes.apps.ClientesConfig",
    "apps.adminpanel.apps.AdminpanelConfig",
    "apps.productos.apps.ProductosConfig",
    "apps.pedidos.apps.PedidosConfig",
    "apps.usuarios.apps.UsuariosConfig",
    "apps.analitica.apps.AnaliticaConfig",
    "apps.recomendacion.apps.RecomendacionConfig",
    "apps.reporting.apps.ReportingConfig",
]

AUTH_USER_MODEL = "usuarios.Usuario"


# =========================
# Middleware
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Debe ubicarse después de SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# CORS
# =========================

def get_configured_origins(*environment_variables):
    origins = []
    for variable in environment_variables:
        origins.extend(
            origin.strip().rstrip("/")
            for origin in os.getenv(variable, "").split(",")
            if origin.strip()
        )
    return list(dict.fromkeys(origins))


development_origins = (
    "http://localhost:4200",
    "http://127.0.0.1:4200",
)

configured_origins = get_configured_origins(
    "CORS_ALLOWED_ORIGINS",
    "FRONTEND_URL",
    "FRONTEND_URLS",
)
default_frontend_origins = (
    development_origins
    if DEBUG
    else ("https://super-ecommerce-el-8g1tweom9-pablodev1.vercel.app",)
)
CORS_ALLOWED_ORIGINS = list(dict.fromkeys(
    [*configured_origins, *default_frontend_origins]
))

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

CORS_ALLOW_METHODS = list(default_methods)


# =========================
# CSRF y cookies
# =========================

CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(
    [
        *get_configured_origins(
            "CSRF_TRUSTED_ORIGINS",
            "FRONTEND_URL",
            "FRONTEND_URLS",
        ),
        *default_frontend_origins,
    ]
))

COOKIE_SAMESITE = os.getenv(
    "COOKIE_SAMESITE", "Lax" if DEBUG else "None"
)

CSRF_COOKIE_SAMESITE = COOKIE_SAMESITE
SESSION_COOKIE_SAMESITE = COOKIE_SAMESITE

CSRF_COOKIE_HTTPONLY = False

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

# Render utiliza un proxy HTTPS delante de Django.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# =========================
# URLs y WSGI
# =========================

ROOT_URLCONF = "ecommerce.urls"

WSGI_APPLICATION = "ecommerce.wsgi.application"


# =========================
# Templates
# =========================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]


# =========================
# Base de datos
# =========================

# Se conserva SQLite y la ubicación actual del archivo.
# Si settings.py está en backend/ecommerce/settings.py,
# BASE_DIR apunta a la carpeta backend.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================
# Validación de contraseñas
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


# =========================
# Internacionalización
# =========================

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True
USE_TZ = True


# =========================
# Archivos estáticos
# =========================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise comprime y sirve los archivos estáticos
# recopilados mediante collectstatic.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# =========================
# Archivos multimedia
# =========================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =========================
# Clave primaria predeterminada
# =========================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Django REST Framework
# =========================

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],

    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),

    "PAGE_SIZE": 15,

    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
    ],
}
