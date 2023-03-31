from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from dotenv import load_dotenv
import os


load_dotenv()

urlpatterns = [
    path('', include('quiz.urls')),
    path(os.environ.get('SECRET_ADMIN_URL') + 'admin/', admin.site.urls),
    path('__reload__', include('django_browser_reload.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
