from os.path import dirname, join, abspath


def project_path(path):
    return abspath(join(dirname(__file__), path))


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_otp',
    'django_otp.plugins.otp_static',

    'test15.app',
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

SECRET_KEY = '9xZjgb6lM998dPRNQ3j7au86X5ZL17Jtme5N910Cp06u7j0QLWara6BH7N90clGQ'

ROOT_URLCONF = 'test15.urls'

AUTH_USER_MODEL = 'app.TestUser'
