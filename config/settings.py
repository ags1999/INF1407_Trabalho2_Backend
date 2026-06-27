"""
Configurações do projeto (backend - API REST).

Backend da aplicação "Minha Estante" - um gerenciador de biblioteca pessoal.
Expõe uma API REST (sem HTML/CSS/JS) consumida por um frontend separado.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env (se existir)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv(
    'SECRET_KEY',
)

# Em produção, defina DEBUG=False via variável de ambiente
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Hosts permitidos (lista separada por vírgula na variável de ambiente)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ---------------------------------------------------------------------------
# Aplicações
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bibliotecas de terceiros
    'rest_framework',                 # Django REST Framework
    'rest_framework_simplejwt',       # Autenticação via tokens JWT
    'drf_spectacular',                # Geração do schema OpenAPI / Swagger
    'corsheaders',                    # Liberação de CORS para o frontend

    # Aplicação local
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # Deve vir o mais alto possível
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Serve arquivos estáticos em produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
# Usa SQLite por padrão (simples para desenvolvimento). Em produção, é possível
# apontar para um PostgreSQL via variável de ambiente DATABASE_URL.
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Suporte simples a PostgreSQL (formato: postgres://user:pass@host:port/db)
    import dj_database_url  # type: ignore
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ---------------------------------------------------------------------------
# Validação de senhas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Modelo de usuário customizado (login por e-mail)
AUTH_USER_MODEL = 'core.User'

# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Arquivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Autenticação padrão por token JWT
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Por padrão, todos os endpoints exigem autenticação (endpoints públicos
    # liberam explicitamente o acesso com AllowAny).
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # drf-spectacular cuida da geração do schema (Swagger / OpenAPI)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Configuração dos tokens JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Configuração do Swagger / OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'Minha Estante - API',
    'DESCRIPTION': (
        'API REST para gerenciamento de uma biblioteca pessoal de livros. '
        'Permite buscar livros na API do Google Books, salvar na estante do '
        'usuário, editar anotações e remover livros (CRUD completo). '
        'A autenticação é feita por tokens JWT.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# ---------------------------------------------------------------------------
# CORS (permite que o frontend separado consuma a API)
# ---------------------------------------------------------------------------
# Lista de origens permitidas (URLs do frontend), separadas por vírgula.
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000',
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# E-mail (usado para ativação de conta e recuperação de senha)
# ---------------------------------------------------------------------------
# Em desenvolvimento, os e-mails são impressos no console.
# Em produção, configure SMTP via variáveis de ambiente.
if os.getenv('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'nao-responda@minhaestante.com'

# URL do frontend (usada para montar links nos e-mails de ativação/recuperação)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5500')

# Chave da API do Google Books (opcional, mas recomendada)
GBOOKS_API_KEY = os.getenv('GBOOKS_API_KEY', '')

CSRF_TRUSTED_ORIGINS = [
    o for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

