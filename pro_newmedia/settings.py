
from __future__ import annotations

import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

from decouple import Csv, config

logger = logging.getLogger(__name__)

# PyMySQL como substituto do mysqlclient (sem dependências de sistema)
try:
    import pymysql
    # Django 6 exige mysqlclient>=2.2.1; PyMySQL reporta 1.x então sobrescrevemos
    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.__version__ = "2.2.1"
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

SECRET_KEY = config("DJANGO_SECRET_KEY", default=None) or config("SECRET_KEY")

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
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://igeracao.com.br",
    "https://www.igeracao.com.br",
    "https://allmedias-production.up.railway.app",
    "https://*.railway.app",
]

# Lendo variáveis de hosts e origens confiáveis, aceitando tanto os nomes antigos quanto os novos
_extra_hosts = [
    h.strip() for h in config("ALLOWED_HOSTS", default=config("DJANGO_ALLOWED_HOSTS", default=""), cast=Csv()) if h.strip()
]

_extra_origins = []
for o in config("CSRF_TRUSTED_ORIGINS", default=config("DJANGO_CSRF_TRUSTED_ORIGINS", default=""), cast=Csv()):
    origin = o.strip()
    if origin:
        # Django 4+ exige o protocolo (https://)
        if not origin.startswith(('http://', 'https://')):
            origin = f'https://{origin}'
        _extra_origins.append(origin)

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

print(f"[settings] DATABASE_URL present: {bool(DATABASE_URL)}", file=sys.stderr)
if DATABASE_URL:
    # Log a redacted version of the URL for debugging (hide password)
    try:
        _url_redacted = urlparse(DATABASE_URL)
        print(
            f"[settings] DATABASE_URL scheme={_url_redacted.scheme!r} "
            f"host={_url_redacted.hostname!r} "
            f"port={_url_redacted.port!r} "
            f"db={_url_redacted.path.lstrip('/')!r}",
            file=sys.stderr,
        )
    except Exception as _e:
        print(f"[settings] Could not redact DATABASE_URL for logging: {_e}", file=sys.stderr)

    try:
        url = urlparse(DATABASE_URL)
        ENGINE_MAP = {
            "mysql": "django.db.backends.mysql",
            "mysql2": "django.db.backends.mysql",
            "postgresql": "django.db.backends.postgresql",
            "postgres": "django.db.backends.postgresql",
        }
        engine = ENGINE_MAP.get(url.scheme)
        if not engine:
            raise ValueError(
                f"Unsupported DATABASE_URL scheme {url.scheme!r}. "
                f"Expected one of: {list(ENGINE_MAP.keys())}"
            )
        if not url.hostname:
            raise ValueError("DATABASE_URL is missing a hostname.")
        if not url.path or url.path == "/":
            raise ValueError("DATABASE_URL is missing a database name (path component).")

        db_config = {
            "ENGINE": engine,
            "NAME": url.path.lstrip("/"),
            "USER": url.username or "",
            "PASSWORD": url.password or "",
            "HOST": url.hostname,
            "PORT": str(url.port or ""),
        }
        # MySQL-specific options
        if "mysql" in engine:
            db_config["OPTIONS"] = {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        DATABASES = {"default": db_config}
        print(
            f"[settings] Database configured: engine={engine!r} "
            f"db={db_config['NAME']!r} host={db_config['HOST']!r}",
            file=sys.stderr,
        )
    except Exception as exc:
        print(f"[settings] ERROR parsing DATABASE_URL: {exc}", file=sys.stderr)
        raise RuntimeError(
            f"Failed to parse DATABASE_URL. Refusing to start with an invalid "
            f"database configuration. Original error: {exc}"
        ) from exc

# In production (DEBUG=False), SQLite is not supported — Railway has no persistent disk.
# If DATABASES is still pointing at SQLite at this point, something went wrong.
_db_engine = DATABASES.get("default", {}).get("ENGINE", "")
if not DEBUG and _db_engine == "django.db.backends.sqlite3":
    raise RuntimeError(
        "DATABASES is configured to use SQLite3 but DEBUG=False (production mode). "
        "SQLite3 is not supported in production on Railway because there is no "
        "persistent storage. Please set the DATABASE_URL environment variable to a "
        "valid MySQL or PostgreSQL connection string."
    )


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
_staticfiles_backend = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
    if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage"
)

USE_S3_STORAGE = config("USE_S3_STORAGE", default=True, cast=bool)

if USE_S3_STORAGE:
    AWS_ACCESS_KEY_ID        = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY    = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME  = config("AWS_STORAGE_BUCKET_NAME", default="allmedias-prod")
    AWS_S3_REGION_NAME       = config("AWS_S3_REGION_NAME", default="us-west-1")
    AWS_S3_ENDPOINT_URL      = config("AWS_S3_ENDPOINT_URL", default="https://s3.us-west-1.wasabisys.com")
    AWS_S3_FILE_OVERWRITE    = False
    AWS_DEFAULT_ACL          = "public-read"   # arquivos públicos (imagens/mídias)
    AWS_QUERYSTRING_AUTH     = False            # URLs limpas sem token expirado
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    STORAGES = {
        "default":     {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": _staticfiles_backend},
    }

    # URL pública das mídias no Wasabi
    MEDIA_URL = f"https://s3.us-west-1.wasabisys.com/allmedias-prod/"


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

# ===================================================================
# CONFIGURAÇÕES DE EMAIL - SENDGRID
# ===================================================================
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='AllMedias <noreply@allmedias.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 10

# ===================================================================
# SEGURANÇA - DESABILITAR HTTPS EM DESENVOLVIMENTO
# ===================================================================
# Necessário no Railway para Django reconhecer requests HTTPS atrás de proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Ativa HTTPS obrigatório e Secure Cookies apenas quando não estamos em ambiente de desenvolvimento
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

