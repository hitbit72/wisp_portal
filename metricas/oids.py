"""
Mapa de OIDs SNMP del servicio de monitorización.

Estructura:
- `OIDS_GENERICO`: SNMPv2-MIB / UCD (sistema, memoria, interfaces).
- `OIDS_MIKROTIK`: MIB MTIK (RouterOS) para CPU/RAM/uptime.
- `OIDS_UBNT_AIRMAX`: MIB de Ubiquiti airOS para radio y clientes.

Los OIDs son "básicos" para empezar y se deben validar contra equipos reales
según marca/modelo. Se puede sobrescribir el mapa por dispositivo desde
`Dispositivo.atributos_extra['oids']` (dict métrica -> OID) o ampliar desde
`settings.METRICAS_OIDS_POR_MARCA` para una marca completa.
"""

from django.conf import settings

OIDS_GENERICO = {
    'uptime': '1.3.6.1.2.1.1.3.0',        # sysUpTime (hundredths de segundo)
    'mem_total': '1.3.6.1.4.1.2021.4.5.0',   # memTotalReal (bytes) - UCD
    'mem_libre': '1.3.6.1.4.1.2021.4.6.0',   # memAvailReal (bytes) - UCD
    'if_descr': '1.3.6.1.2.1.2.2.1.2',       # ifTable/ifDescr (walk)
    'if_oper': '1.3.6.1.2.1.2.2.1.8',        # ifTable/ifOperStatus (walk)
}

OIDS_MIKROTIK = {
    'cpu': '1.3.6.1.4.1.14988.1.1.1.2.1.1.0',      # mtikSystemCpu (%)
    'mem_libre': '1.3.6.1.4.1.14988.1.1.1.2.1.2.0',  # mtikSystemFreeMemory
    'mem_total': '1.3.6.1.4.1.14988.1.1.1.2.1.3.0',  # mtikSystemTotalMemory
    'uptime': '1.3.6.1.4.1.14988.1.1.1.2.1.4.0',     # mtikSystemUptime (segundos)
}

OIDS_UBNT_AIRMAX = {
    'signal': '1.3.6.1.4.1.41112.1.4.5.1.1.0',   # señal (dBm)
    'ccq': '1.3.6.1.4.1.41112.1.4.5.1.2.0',      # CCQ (%)
    'rx': '1.3.6.1.4.1.41112.1.4.5.1.3.0',       # tasa Rx (bps)
    'tx': '1.3.6.1.4.1.41112.1.4.5.1.4.0',       # tasa Tx (bps)
    'frequency': '1.3.6.1.4.1.41112.1.4.5.1.5.0',  # frecuencia (MHz)
    'channel': '1.3.6.1.4.1.41112.1.4.5.1.6.0',    # canal
    'clients': '1.3.6.1.4.1.41112.1.4.6.1',        # tabla de estaciones (walk, contar)
    'rx_dbm': '1.3.6.1.4.1.41112.1.4.6.1.7.0',     # Rx dBm de la estación (si aplica)
    'tx_dbm': '1.3.6.1.4.1.41112.1.4.6.1.8.0',     # Tx dBm de la estación (si aplica)
    'snr': '1.3.6.1.4.1.41112.1.4.5.1.7.0',        # SNR (dB)
}

VENDOR_MAP = {
    'mikrotik': OIDS_MIKROTIK,
    'ubiquiti': OIDS_UBNT_AIRMAX,
}


def oids_para_dispositivo(dispositivo):
    """
    Devuelve el mapa de OIDs combinado para un dispositivo: genéricos +
    los de su marca, ampliable por marca desde settings y sobrescribible
    por dispositivo desde `atributos_extra['oids']`.
    """
    por_marca = settings.METRICAS_OIDS_POR_MARCA or {}
    oids = {}
    oids.update(OIDS_GENERICO)
    oids.update(VENDOR_MAP.get(dispositivo.marca, {}))
    oids.update(por_marca.get(dispositivo.marca, {}))
    extra = (dispositivo.atributos_extra or {}).get('oids') or {}
    oids.update(extra)
    return oids