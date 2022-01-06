# django-otp test project

import os
from os.path import abspath, dirname, join

from django.core.exceptions import ImproperlyConfigured


def project_path(path):
    return abspath(join(dirname(__file__), path))


DEBUG = True

backend = os.getenv('DB_BACKEND', 'sqlite3')
if backend == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': project_path('db.sqlite3'),
        }
    }
elif backend == 'postgresql':
    # SQLite lacks some features necessary for advanced concurrency tests.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'django_otp_test',
            'USER': 'postgres',
        }
    }
else:
    raise ImproperlyConfigured("Unrecognized value for DB_BACKEND: {}".format(backend))


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_otp',
    'django_otp.plugins.otp_email',
    'django_otp.plugins.otp_hotp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'test_project.backends.DummyBackend',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            project_path('templates'),
        ],
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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SECRET_KEY = 'PWuluw4x48GkT7JDPzlDQsBJC8pjIIiqodW9MuMYcU315YEkGJL41i5qooJsg3Tt'

ROOT_URLCONF = 'test_project.urls'

STATIC_URL = '/static/'

USE_TZ = True
