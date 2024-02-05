from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.views import generic
from django.urls import re_path

from gestion.admin import MemberAdmin


app_name = 'gestion'
urlpatterns = [
    path('', views.list, name="home"),
    path('list', views.list, name="list"),
    path('cargos', views.cargos, name="cargos"),
    path('cargos_capacitacion', views.cargos_capacitacion, name="cargos_capacitacion"),
    path('member/<pk>', views.MemberDetailView.as_view(), name='member-detail'),
    path(r'update-grupo/<int:pk>/', views.update_grupo, name="update_grupo"),
    path('organigrama', views.organigrama, name="organigrama"),
    re_path(r'^exportar_organigrama/(?P<region>\w+)/$', views.exportar_organigrama, name="exportar_organigrama"),
    re_path(r'^getEstructura/$', views.get_estructura),
    re_path(r'^getCargosRegion/$', views.get_data),
    re_path(r'^getRegiones/$', views.regiones),
    re_path(r'^list/(?P<q>\w+)/$', views.list, name="list_filter"),
    re_path(r'^getList', views.get_list),
    path(r'reactivar/<int:pk>/', views.reactivar, name="reactivar"),
    path(r'deshacer_baja/<int:pk>/', views.deshacer_baja, name="deshacer_baja"),
    path(r'dar_baja_lopd/<int:pk>/', views.dar_baja_lopd, name="dar_baja_lopd"),
    path(r'anadir-cargo/<int:pk>/', views.añadir_cargo, name="anadir-cargo"),
    path(r'anadir-cargo-capacitacion/<int:pk>/', views.añadir_cargo_capacitacion, name="anadir-cargo-capacitacion"),
    path(r'dar-baja-cargo/<int:pk>/', views.dar_baja_cargo, name="dar-baja-cargo"),
    path(r'panel', views.panel, name="panel"),
    path(r'dar-baja-cargo-capacitacion/<int:pk>/', views.dar_baja_cargo_capacitacion, name="dar-baja-cargo-capacitacion"),
    path(r'logout_view/(?P<expired_user>\w+)/', views.logout_view, name='logout_view'),
    path('<pk>/delete/', views.MemberDeleteView.as_view()),
    path(r'delete-member/<int:pk>/', views.delete_member),
    re_path(r'^getMotivosBaja/$', views.get_motivos_baja),
    path(r'registration/update.html', views.change_password, name='cambia-pass'),
    path('datos_suscripcion', views.data_subcriptions, name='data-suscriptions'),
    path('datos_suscripcion_cargo', views.data_subcriptions_cargo, name='data-suscriptions_cargo'),
    path('datos_suscripcion_capacitacion', views.data_subcriptions_capacitacion, name='data-suscriptions_capacitacion')
]
