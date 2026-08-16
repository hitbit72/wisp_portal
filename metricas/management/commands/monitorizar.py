"""
`manage.py monitorizar`: consulta por SNMP todos los dispositivos con IP de
gestión y comunidad, guarda una métrica por dispositivo y aplica alarmas.

Para ejecutarse cada minuto, planificar una tarea con el planificador del
SO o el worker de fondo del proyecto.

Ejemplo de crontab (cada minuto):

    */1 * * * * cd /ruta/wisp_portal && uv run manage.py monitorizar >> /var/log/wispcontrol/metricas.log 2>&1

Uso manual:

    uv run manage.py monitorizar

Si quieres confirmar qué hay realmente en esa columna:

    uv run manage.py shell -c "from red.models import Dispositivo; [print(d.nombre, repr(d.snmp_community)) for d in Dispositivo.objects.all()]"

"""

from django.core.management.base import BaseCommand
from red.models import Dispositivo

from metricas import snmp_client
from metricas.models import DeviceMetrics
from metricas.oids import oids_para_dispositivo
from metricas.services import evaluar_y_aplicar, guardar_metrica

# metrica OID -> campo del modelo (clave 'mem_total'/'mem_libre' -> ram).
CAMPO = {
    'cpu': 'cpu',
    'temperature': 'temperature',
    'power': 'power',
    'rx_dbm': 'rx_dbm',
    'tx_dbm': 'tx_dbm',
    'snr': 'snr',
    'ccq': 'ccq',
    'signal': 'signal',
    'frequency': 'frequency',
    'channel': 'channel',
    'clients': 'clients',
    'rx': 'rx',
    'tx': 'tx',
    'uptime': 'uptime',
}


class Command(BaseCommand):
    help = 'Consulta SNMP a cada dispositivo y guarda métricas + alarmas.'

    def handle(self, *args, **options):
        dispositivos = (
            Dispositivo.objects
            .filter(ip_gestion__isnull=False)
            .exclude(snmp_community__isnull=True)
            .exclude(escanear=False)
        )
        total, ok = len(dispositivos), 0
        if not total:
            self.stdout.write(self.style.WARNING(
                'No hay dispositivos con IP de gestión.'))
        for dispositivo in dispositivos:
            if self._procesar(dispositivo):
                ok += 1
        self.stdout.write(self.style.SUCCESS(
            f'Monitorizados {ok} de {total} dispositivos.'))

    def _procesar(self, dispositivo):
        escalares = {
            k: v for k, v in oids_para_dispositivo(dispositivo).items()
            if k not in ('if_descr', 'if_oper')
        }
        try:
            resultado = snmp_client.consultar_escalares(dispositivo, escalares)
            puertos = snmp_client.consultar_if_table(dispositivo)
            status = DeviceMetrics.Status.OK
        except snmp_client.SnmpError as exc:
            self.stdout.write(
                self.style.ERROR(f'[{dispositivo.nombre}] {exc}'))
            resultado, puertos = {}, []
            mensaje = str(exc).lower()
            status = (
                DeviceMetrics.Status.TIMEOUT
                if 'time out' in mensaje or 'timed out' in mensaje
                else DeviceMetrics.Status.ERROR
            )

        datos = self._construir_datos(dispositivo, resultado)
        datos['puertos'] = puertos
        datos['status'] = status

        metrica = guardar_metrica(dispositivo, **datos)
        evaluar_y_aplicar(dispositivo, metrica)
        self.stdout.write(self.style.SUCCESS(
            f'[{dispositivo.nombre}] {status}'))
        return status == DeviceMetrics.Status.OK

    def _construir_datos(self, dispositivo, resultado):
        datos = {}
        if 'mem_total' in resultado and 'mem_libre' in resultado:
            total, _ = resultado['mem_total']
            libre, _ = resultado['mem_libre']
            if total:
                datos['ram'] = round((1 - libre / total) * 100, 2)
        if 'memory_p' in resultado:
            datos['ram'] = resultado['memory_p']
        if 'cpu_p' in resultado:
            datos['cpu'] = resultado['cpu_p']
        for metrica, (numero, texto) in resultado.items():
            campo = CAMPO.get(metrica)
            if not campo:
                continue
            if metrica == 'uptime':
                # sysUpTime está en centésimas; MTIK en segundos.
                valor = numero / 100 if dispositivo.marca != Dispositivo.Marca.MIKROTIK else numero
                datos['uptime'] = int(valor)
            elif campo == 'channel':
                datos['channel'] = texto or ''
            elif numero is not None:
                datos[campo] = numero
        return datos