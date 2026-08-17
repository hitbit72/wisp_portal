from django.contrib import admin

from .models import Alarma, DeviceMetrics


@admin.register(DeviceMetrics)
class DeviceMetricsAdmin(admin.ModelAdmin):
    list_display = ('device', 'timescan', 'status', 'cpu', 'ram', 'frequency', 'signal', 'clients', 'uptime')
    list_filter = ('status', 'device__tipo', 'device__marca')
    date_hierarchy = 'timestamp'
    search_fields = ('device__nombre',)
    readonly_fields = ('device', 'timestamp', 'timescan')
    list_select_related = ('device',)


@admin.register(Alarma)
class AlarmaAdmin(admin.ModelAdmin):
    list_display = ('device', 'titulo', 'regla', 'estado', 'creada_en', 'resuelta_en')
    list_filter = ('estado', 'regla', 'device__tipo')
    search_fields = ('device__nombre', 'titulo', 'texto')
    list_select_related = ('device',)
    readonly_fields = ('device', 'regla', 'titulo', 'texto', 'creada_en', 'resuelta_en')