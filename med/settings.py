
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


# ==========================================
# ОСНОВНЫЕ ПУТИ
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Локальные переменные окружения.
# Поддерживаем оба возможных расположения .env.
load_dotenv(BASE_DIR / '.env')
load_dotenv(BASE_DIR.parent / '.env', override=False)


# ==========================================
# БЕЗОПАСНОСТЬ
# ==========================================

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = os.getenv(
    "DJANGO_DEBUG", "False"
).lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "auramed-lemc.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://auramed-lemc.onrender.com",
]

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


# ==========================================
# POSTGRESQL
# ==========================================

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}


# ==========================================
# УСТАНОВЛЕННЫЕ ПРИЛОЖЕНИЯ
# ==========================================

INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary
    'cloudinary_storage',
    'cloudinary',

    # AuraMed
    'main',
    'doctors',
]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Раздача статических файлов на Render
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==========================================
# URL И ШАБЛОНЫ
# ==========================================

ROOT_URLCONF = 'med.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'med.wsgi.application'


# ==========================================
# ПРОВЕРКА ПАРОЛЕЙ
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# ==========================================
# ЯЗЫК И ВРЕМЯ
# ==========================================

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True


# ==========================================
# CLOUDINARY
# ==========================================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}


# ==========================================
# СТАТИЧЕСКИЕ ФАЙЛЫ
# ==========================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ==========================================
# ЗАГРУЖАЕМЫЕ ФАЙЛЫ
# ==========================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==========================================
# ХРАНИЛИЩА
# ==========================================

STORAGES = {

    # Фотографии врачей и услуг
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.'
            'MediaCloudinaryStorage'
        ),
    },

    # CSS, JavaScript, файлы Django Admin
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.'
            'CompressedManifestStaticFilesStorage'
        ),
    },
}


# ==========================================
# EMAIL
# ==========================================

MAILERS = {
    'default': {
        'BACKEND': (
            'django.core.mail.backends.'
            'console.EmailBackend'
        ),
    },
}
