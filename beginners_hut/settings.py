
from pathlib import Path
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# SECURITY SETTINGS
# =====================================================

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-change-this-key-for-local-development'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = (
    ['*'] if DEBUG
    else [
        'beginnershut.com',
        'www.beginnershut.com',
    ]
)


# =====================================================
# APPLICATIONS
# =====================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',

    'compressor',
    'ckeditor',

    'admin_panel',
    'blog',
    'portfolio',
]

SITE_ID = 1


# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =====================================================
# URLS AND WSGI
# =====================================================

ROOT_URLCONF = 'beginners_hut.urls'

WSGI_APPLICATION = 'beginners_hut.wsgi.application'


# =====================================================
# TEMPLATES
# =====================================================

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
                'admin_panel.context_processors.admin_chrome',
            ],
        },
    },
]


# =====================================================
# DATABASE
# =====================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =====================================================
# PASSWORD VALIDATION
# =====================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =====================================================
# INTERNATIONALIZATION
# =====================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True


# =====================================================
# STATIC FILES
# =====================================================

STATIC_URL = '/static/'

# Source directory for your project-level static files.
# Make sure this directory exists.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Destination directory used by collectstatic.
# This must be different from STATICFILES_DIRS.
STATIC_ROOT = BASE_DIR / 'staticfiles'


# =====================================================
# DJANGO COMPRESSOR
# =====================================================

COMPRESS_ROOT = STATIC_ROOT

COMPRESS_ENABLED = DEBUG

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]


# =====================================================
# MEDIA FILES
# =====================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# =====================================================
# EMAIL SETTINGS
# =====================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_HOST_USER = os.environ.get(
    'EMAIL_HOST_USER',
    'asfakulthoha@gmail.com'
)

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

EMAIL_USE_TLS = True

EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# =====================================================
# DEFAULT PRIMARY KEY
# =====================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =====================================================
# URL SETTINGS
# =====================================================

APPEND_SLASH = True


