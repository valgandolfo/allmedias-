import os
import socket
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# --- 1. CAMINHOS E AMBIENTE ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# --- 2. SEGURANÇA ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-local')

# DEBUG: Se no Railway houver a variável DEBUG=False, ele desativa. Caso contrário, True.
DEBUG = os.getenv('DEBUG', 'False').upper() == 'False'

# ALLOWED_HOSTS: domínio público, Railway e localhost (Host ausente = Django devolve 400)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    '0.0.0.0',
    'www.igeracao.com.br',
    'igeracao.com.br',
    '.igeracao.com.br',
    'web-production-c67ff.up.railway.app',
    '.railway.app',
]

# --- 3. APLICAÇÃO ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'storages',
    'app_igreja',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pro_igreja.urls'
WSGI_APPLICATION = 'pro_igreja.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- 4. BANCO DE DADOS ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.getenv('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# --- 5. ARMAZENAMENTO E ESTÁTICOS ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# MEDIA: Wasabi (S3) quando credenciais existirem; senão disco local.
# Com Wasabi: pasta media/ NÃO é usada — todos os uploads (TBVISUAL, etc.) vão direto ao Wasabi.
_use_wasabi = all([
    os.getenv('AWS_ACCESS_KEY_ID'),
    os.getenv('AWS_SECRET_ACCESS_KEY'),
    os.getenv('AWS_STORAGE_BUCKET_NAME'),
])

# Usado pelas views para mensagens (paróquia/visual): só afirmar "gravado no Wasabi" quando for verdade.
USE_WASABI = _use_wasabi

if _use_wasabi:
    # URLs assinadas (presigned): conta Wasabi sem "public use" → leitura via URL temporária com assinatura.
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": os.getenv('AWS_STORAGE_BUCKET_NAME'),
                "region_name": os.getenv('AWS_S3_REGION_NAME', 'us-east-1'),
                "endpoint_url": os.getenv('AWS_S3_ENDPOINT_URL', 'https://s3.us-east-1.wasabisys.com'),
                "custom_domain": False,
                "querystring_auth": True,
                "querystring_expire": 86400,
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', 'https://s3.us-east-1.wasabisys.com')
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.wasabisys.com/"
    MEDIA_ROOT = ''  # Não usar pasta media/; tudo vem do Wasabi.
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# --- 6. I18N ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 7. CSRF E SEGURANÇA ---
# Django não aceita wildcard; adicione cada origem completa (ex.: https://seu-app.up.railway.app).
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-c67ff.up.railway.app',
]
_extra_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '').strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend(o.strip() for o in _extra_csrf.split(',') if o.strip())

# Proxy (Railway) envia HTTPS via header; necessário para cookies Secure e redirect correto.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Relaxar cookies: se RELAX_COOKIES=1 no ambiente, cookies não usam Secure (site volta a carregar em alguns navegadores).
_relax_cookies = os.getenv('RELAX_COOKIES', '').strip().lower() in ('1', 'true', 'yes')

if DEBUG:
    CSRF_TRUSTED_ORIGINS += ['http://localhost:8000', 'http://127.0.0.1:8000']
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECURE_SSL_REDIRECT = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
elif _relax_cookies:
    # Produção com cookies relaxados (evita “não carrega” no Opera/outros).
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    # Produção com cookies estritos (Secure, só HTTPS).
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# --- 8. AUTENTICAÇÃO E EMAIL ---
AUTHENTICATION_BACKENDS = [
    'app_igreja.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/app_igreja/admin-area/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@igeracao.com.br')