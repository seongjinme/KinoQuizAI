import os
from .base import *
from dotenv import load_dotenv


# Initiate `load_dotenv` to read .env file
load_dotenv()

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    '.vercel.app',
]

INSTALLED_APPS = [
    'tailwind',
    'quiz',
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
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': str(os.getenv('DB_ENGINE')),
        'NAME': str(os.getenv('DB_NAME')),
        'USER': str(os.getenv('DB_USER')),
        'PASSWORD': str(os.getenv('DB_PASSWORD')),
        'HOST': str(os.getenv('DB_HOST')),
        'PORT': str(os.getenv('DB_PORT')),
    }
}

WSGI_APPLICATION = 'vercel_app.wsgi.app'

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = []
SECURE_BROWSER_XSS_FILTER = True
