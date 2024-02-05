from . import views
from django.conf.urls import url


app_name = 'cargos'
urlpatterns = [
    url(r'^get_object_id/', views.get_object_id),
    url(r'^populate_object_id/', views.populate_object_id),
]