from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'
urlpatterns = [
    path(r'login/', auth_views.LoginView.as_view(template_name='accounts/login.html')),
    path('', include('django.contrib.auth.urls')),
]