from django.contrib import admin
from .models import Sector, Dispositivo, Interfaz, Enlace


class InterfazInline(admin.TabularInline):
    model = Interfaz
    extra = 0


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('nombre','poblacion')
    search_fields = ('nombre','poblacion')


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('ip_gestion','nombre', 'tipo', 'marca', 'modelo', 'sector', 'estado', 'cliente')
    list_filter = ('tipo', 'marca', 'estado', 'sector')
    search_fields = ('nombre', 'ip_gestion', 'mac_address', 'cliente')
    inlines = [InterfazInline]


@admin.register(Interfaz)
class InterfazAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'nombre', 'tipo', 'estado', 'ip_address')
    list_filter = ('tipo', 'estado')
    search_fields = ('nombre', 'dispositivo__nombre', 'ip_address')


@admin.register(Enlace)
class EnlaceAdmin(admin.ModelAdmin):
    list_display = ('dispositivo_origen', 'dispositivo_destino', 'tipo', 'ancho_banda_mbps')
    list_filter = ('tipo',)
