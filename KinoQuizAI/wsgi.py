import os
from django.core.wsgi import get_wsgi_application

# Get the environment setting value
environment = os.environ.get('ENVIRONMENT_SETTING', 'development')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'KinoQuizAI.settings.{environment}')

application = get_wsgi_application()
app = application
