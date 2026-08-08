from django.urls import path

from . import views

app_name = 'red'

urlpatterns = [
    # Sectores
    path('', views.lista_sectores, name='lista'),
    path('sectores/nuevo/', views.form_sector, name='nuevo_sector'),
    path('sectores/<int:pk>/', views.detalle_sector, name='detalle_sector'),
    path('sectores/<int:pk>/editar/', views.form_sector, name='editar_sector'),
    path('sectores/<int:pk>/eliminar/', views.eliminar_sector, name='eliminar_sector'),
    # Dispositivos (vista global + CRUD)
    path('dispositivos/', views.lista_dispositivos, name='lista_dispositivos'),
    path('sectores/<int:sector_pk>/dispositivos/nuevo/', views.nuevo_dispositivo, name='nuevo_dispositivo'),
    path('dispositivos/<int:pk>/', views.detalle_dispositivo, name='detalle_dispositivo'),
    path('dispositivos/<int:pk>/editar/', views.editar_dispositivo, name='editar_dispositivo'),
    path('dispositivos/<int:pk>/eliminar/', views.eliminar_dispositivo, name='eliminar_dispositivo'),
    # Interfaces
    path('dispositivos/<int:dispositivo_pk>/interfaces/nueva/', views.nueva_interfaz, name='nueva_interfaz'),
    path('interfaces/<int:pk>/editar/', views.editar_interfaz, name='editar_interfaz'),
    path('interfaces/<int:pk>/eliminar/', views.eliminar_interfaz, name='eliminar_interfaz'),
    # Enlaces
    path('dispositivos/<int:dispositivo_pk>/enlaces/nuevo/', views.nuevo_enlace, name='nuevo_enlace'),
    path('enlaces/<int:pk>/editar/', views.editar_enlace, name='editar_enlace'),
    path('enlaces/<int:pk>/eliminar/', views.eliminar_enlace, name='eliminar_enlace'),
]