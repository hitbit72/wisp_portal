"""
Servicio del módulo metricas: guarda la métrica capturada, sincroniza las
alarmas con las reglas detectadas y actualiza el estado del dispositivo.
"""

from django.conf import settings
from django.utils import timezone

from eventos.models import Evento
from eventos.services import registrar_evento
from red.models import Dispositivo

from .models import Alarma, DeviceMetrics
from .reglas import REGLA_INACTIVO, REGLA_NIVEL, evaluar

MODULO = 'metricas'


def guardar_metrica(dispositivo, **datos):
    """Crea la fila DeviceMetrics. Solo la usa el servicio de monitorización."""
    datos.setdefault('status', DeviceMetrics.Status.OK)
    return DeviceMetrics.objects.create(device=dispositivo, **datos)


def evaluar_y_aplicar(dispositivo, metrica):
    """Evalúa las reglas sobre la métrica recién creada y aplica alarmas y
    estado. Devuelve dict {nuevas, resueltas} con las alarmas tocadas."""
    anterior = (
        DeviceMetrics.objects.filter(device=dispositivo, pk__lt=metrica.pk)
        .order_by('-pk').first()
    )
    activas = evaluar(dispositivo, metrica, anterior, settings.METRICAS_ALARMAS)
    resultados = _sincronizar_alarmas(dispositivo, activas)
    _actualizar_estado(dispositivo, activas)
    return resultados


def _sincronizar_alarmas(dispositivo, detectadas):
    """Alta de las reglas nuevas, resolución de las que ya no se cumplen."""
    activas = Alarma.objects.filter(device=dispositivo, estado=Alarma.Estado.ACTIVA)
    reglas_activas = dict(activas.values_list('regla', 'pk'))
    detectadas = {a['regla']: a for a in detectadas}

    resultados = {'nuevas': [], 'resueltas': []}

    for regla, pk in reglas_activas.items():
        if regla in detectadas:
            continue
        alarma = Alarma.objects.get(pk=pk)
        alarma.estado = Alarma.Estado.RESUELTA
        alarma.resuelta_en = timezone.now()
        alarma.save(update_fields=['estado', 'resuelta_en'])
        registrar_evento(
            MODULO,
            f'Alarma resuelta: {alarma.titulo}',
            f'{dispositivo.nombre} · {alarma.texto}',
            nivel=Evento.Nivel.NOTICE,
        )
        resultados['resueltas'].append(alarma)

    for regla, datos in detectadas.items():
        alarma = Alarma.objects.create(
            device=dispositivo, regla=regla, titulo=datos['titulo'], texto=datos['texto'],
        )
        registrar_evento(
            MODULO, alarma.titulo,
            f'{dispositivo.nombre} · {alarma.texto}',
            nivel=REGLA_NIVEL.get(regla, Evento.Nivel.WARNING),
        )
        resultados['nuevas'].append(alarma)
    return resultados


def _actualizar_estado(dispositivo, detectadas):
    """Pasa a 'inactivo' cuando hay una regla que marca el dispositivo y
    vuelve a 'activo' cuando las reglas se normalizan. Solo se tocan los
    estados operativos 'activo'/'inactivo' (mantenimiento, instalación,
    retirado quedan intactos)."""
    if dispositivo.estado not in (Dispositivo.Estado.ACTIVO, Dispositivo.Estado.INACTIVO):
        return
    inactivo = any(a['regla'] in REGLA_INACTIVO for a in detectadas)

    if inactivo and dispositivo.estado == Dispositivo.Estado.ACTIVO:
        dispositivo.estado = Dispositivo.Estado.INACTIVO
        dispositivo.save(update_fields=['estado'])
        registrar_evento(
            MODULO, f'Dispositivo sin conectividad: {dispositivo.nombre}',
            'Se marcó como inactivo por falta de respuesta SNMP.',
            nivel=Evento.Nivel.CRITICAL,
        )
    elif not inactivo and dispositivo.estado == Dispositivo.Estado.INACTIVO:
        dispositivo.estado = Dispositivo.Estado.ACTIVO
        dispositivo.save(update_fields=['estado'])
        registrar_evento(
            MODULO, f'Dispositivo recuperado: {dispositivo.nombre}',
            'Vuelve a responder correctamente a SNMP.',
            nivel=Evento.Nivel.NOTICE,
        )