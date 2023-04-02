import environ
import io
import os
from google.cloud import secretmanager
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Set environment variables
env = environ.Env()
# env_file = os.path.join(BASE_DIR, '.env')
env_file = os.path.join(BASE_DIR, 'KinoQuizAI', '.env')
env.read_env(env_file)

# Read a local .env file
if os.path.isfile(env_file):
    env.read_env(env_file)

# Pull .env file from GCP Secret Manager
elif os.environ.get('GOOGLE_CLOUD_PROJECT', None):
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get('SETTINGS_NAME', 'django_settings')
    name = f'projects/{project_id}/secrets/{settings_name}/versions/latest'
    payload = client.access_secret_version(name=name).payload.data.decode('UTF-8')

    env.read_env(io.StringIO(payload))

# Neither option is available, raise exception
else:
    raise Exception('No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.')

# Application definition
SECRET_KEY = env('SECRET_KEY')

INSTALLED_APPS = [
    'tailwind',
    'quiz',
    'django_browser_reload',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

WSGI_APPLICATION = 'KinoQuizAI.wsgi.application'
ROOT_URLCONF = "KinoQuizAI.urls"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Initiate Django-Tailwind

TAILWIND_APP_NAME = 'quiz'
INTERNAL_IPS = [
    '127.0.0.1',
]


# Authentication settings for User model in 'quiz' app

AUTH_USER_MODEL = 'quiz.User'
LOGIN_URL = '/login/'


# CSRF protection setting

CSRF_TRUSTED_ORIGINS = []
