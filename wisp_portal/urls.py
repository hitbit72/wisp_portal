from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('clientes/', include('clientes.urls')),
    path('mikrotik/', include('mikrotik.urls')),
]
