
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("DJANGO_SECRET_KEY")

DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)

# Hosts e origins obrigatórios — sempre presentes independente de env vars
_ALLOWED_HOSTS_BASE = [
    "localhost",
    "127.0.0.1",
    "igeracao.com.br",
    "www.igeracao.com.br",
    "allmedias-production.up.railway.app",
    ".railway.app",
]

_CSRF_ORIGINS_BASE = [
    "http://localhost",
    "http://127.0.0.1",
    "https://igeracao.com.br",
    "https://www.igeracao.com.br",
    "https://allmedias-production.up.railway.app",
]

# Permite extensão via env var (ex.: novo domínio no futuro)
_extra_hosts = [h.strip() for h in config("DJANGO_ALLOWED_HOSTS", default="", cast=Csv()) if h.strip()]
_extra_origins = [o.strip() for o in config("DJANGO_CSRF_TRUSTED_ORIGINS", default="", cast=Csv()) if o.strip()]

ALLOWED_HOSTS = list({*_ALLOWED_HOSTS_BASE, *_extra_hosts})
CSRF_TRUSTED_ORIGINS = list({*_CSRF_ORIGINS_BASE, *_extra_origins})


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps do projeto
    "app_newmedia",
    "app_newmedia.registration",
    "app_newmedia.medias",
    "app_newmedia.anota_ai",
    "app_newmedia.conversor",
    "app_newmedia.transferir",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pro_newmedia.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "pro_newmedia.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    url = urlparse(DATABASE_URL)
    ENGINE_MAP = {
        "mysql": "django.db.backends.mysql",
        "mysql2": "django.db.backends.mysql",
    }
    engine = ENGINE_MAP.get(url.scheme)
    if engine:
        DATABASES = {
            "default": {
                "ENGINE": engine,
                "NAME": url.path.lstrip("/"),
                "USER": url.username or "",
                "PASSWORD": url.password or "",
                "HOST": url.hostname or "",
                "PORT": str(url.port or "3306"),
                "OPTIONS": {
                    "charset": "utf8mb4",
                    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        }


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


LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ===================================================================
# STORAGE - WASABI S3
# ===================================================================
USE_S3_STORAGE = config("USE_S3_STORAGE", default=False, cast=bool)

if USE_S3_STORAGE:
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = "private"
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_SIGNATURE_VERSION = "s3v4"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO
# ===================================================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Backend de autenticação por e-mail
AUTHENTICATION_BACKENDS = [
    'app_newmedia.registration.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # fallback para admin (username)
]

# Email backend (desenvolvimento)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===================================================================
# SEGURANÇA - DESABILITAR HTTPS EM DESENVOLVIMENTO
# ===================================================================
# Necessário no Railway para Django reconhecer requests HTTPS atrás de proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

