# django-otp test project

from os.path import abspath, dirname, join

from django.urls import reverse_lazy

from . import config


def project_path(path):
    return abspath(join(dirname(__file__), path))


cfg = config.load()


DEBUG = True

DATABASES = {
    'default': cfg.get('database') or {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': project_path('db.sqlite3'),
    }
}


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

INSTALLED_APPS.extend(cfg.get('plugins', []))


middleware_pre = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

middleware_post = [
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE = middleware_pre + cfg.get('middleware', []) + middleware_post

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

SECRET_KEY = 'test-key'

ROOT_URLCONF = 'test_project.urls'

STATIC_URL = '/static/'

LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGOUT_REDIRECT_URL = reverse_lazy('home')

OTP_LOGIN_URL = reverse_lazy('login-otp')

USE_TZ = True

for k, v in cfg.get('settings', {}).items():
    globals()[k] = v
