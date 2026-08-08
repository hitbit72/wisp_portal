from django.contrib import admin
from django.urls import path, include

from red.views import lista_dispositivos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('clientes/', include('clientes.urls')),
    path('mikrotik/', include('mikrotik.urls')),
    path('red/', include('red.urls')),
    path('dispositivos/', lista_dispositivos, name='lista_dispositivos'),
]
