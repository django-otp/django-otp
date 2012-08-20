# django-agent-trust test project

from os.path import dirname, join, abspath

def project_path(path):
    return abspath(join(dirname(__file__), path))

DEBUG = True

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_otp',
    'django_otp.plugins.otp_hotp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_email',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATE_DIRS = [
    project_path('templates'),
]

SECRET_KEY = 'cI4AHyAcIKQxcq2hI54YS7Bnn6vbojTxxlTWQdRiA2pky5oz8IEgJ1DcyvCDXnXn'

ROOT_URLCONF = 'urls'
