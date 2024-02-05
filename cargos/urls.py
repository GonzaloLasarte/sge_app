from . import views
from django.urls import path


app_name = 'cargos'
urlpatterns = [
    path(r'^get_object_id/', views.get_object_id),
    path(r'^populate_object_id/', views.populate_object_id),
]