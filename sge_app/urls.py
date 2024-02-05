from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, include
from .views import redirect_view, media
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url('^', include('gestion.urls')),
    url('^', include('cargos.urls')),
    url('admin/', admin.site.urls),
    url('accounts/', include('django.contrib.auth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('media/<int:pk>/<str:filename>', media)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
