import os
from dotenv import load_dotenv

load_dotenv()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KinoQuizAI.settings')

application = get_wsgi_application()
app = application
