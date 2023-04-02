from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path('', include('quiz.urls', namespace='quiz')),
    path(f'{settings.ADMIN_URL}/admin/', admin.site.urls),
    path('__reload__', include('django_browser_reload.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
