import os
from .base import *


DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
]

# Database settings
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
