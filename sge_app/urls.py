from django.contrib import admin
from django.urls import path, include, re_path
from .views import redirect_view, media
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    re_path('^', include('gestion.urls')),
    re_path('^', include('cargos.urls')),
    re_path('admin/', admin.site.urls),
    re_path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path('media/<int:pk>/<str:filename>', media)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
