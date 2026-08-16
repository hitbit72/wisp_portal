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
    'uptime': '1.3.6.1.2.1.1.3.0',           # sysUpTime (hundredths de segundo)
    'sys_name': '1.3.6.1.2.1.1.5.0',         #sysName
    'sys_descr': '1.3.6.1.2.1.1.1.0',        #sysDescription
    'mem_total': '1.3.6.1.4.1.2021.4.5.0',   # memTotalReal (bytes) - UCD
    'mem_libre': '1.3.6.1.4.1.2021.4.6.0',   # memAvailReal (bytes) - UCD
    'cpu_p': '1.3.6.1.4.1.2021.10.1.3.2',    # 5min load average
    'if_descr': '1.3.6.1.2.1.2.2.1.2',       # ifTable/ifDescr (walk)
    'if_oper': '1.3.6.1.2.1.2.2.1.8',        # ifTable/ifOperStatus (walk)
}

OIDS_MIKROTIK = {
    'cpu': '1.3.6.1.4.1.14988.1.1.1.2.1.1.0',      # mtikSystemCpu (%)
    'mem_libre': '1.3.6.1.4.1.14988.1.1.1.2.1.2.0',  # mtikSystemFreeMemory
    'mem_total': '1.3.6.1.4.1.14988.1.1.1.2.1.3.0',  # mtikSystemTotalMemory
    'uptime': '1.3.6.1.4.1.14988.1.1.1.2.1.4.0',     # mtikSystemUptime (segundos)
}

OIDS_UBNT_AIRMAX_ORIGINAL = {
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


OIDS_UBNT_AIRMAX = {
    'cpu_p': '1.3.6.1.4.1.10002.1.1.1.4.2.1.2.2',     # 5 Minute Average
    'ccq': '1.3.6.1.4.1.41112.1.4.5.1.7.1',         # UBNT-AirMAX-MIB::ubntWlStatCcq.1
    'clients': '1.3.6.1.4.1.41112.1.4.5.1.15.1',    # UBNT-AirMAX-MIB::ubntWlStatStaCount.1
    'noise': '1.3.6.1.4.1.41112.1.4.5.1.8.1',       # UBNT-AirMAX-MIB::ubntWlStatNoiseFloor
    'power': '1.3.6.1.4.1.41112.1.4.1.1.6.1',       # UBNT-AirMAX-MIB::ubntRadioTxPower
    'signal': '1.3.6.1.4.1.41112.1.4.5.1.5.1',      # UBNT-AirMAX-MIB::ubntWlStatSignal
    'w_channel': '1.3.6.1.4.1.41112.1.4.5.1.14.1',   # width channel
    'rx': '1.3.6.1.4.1.41112.1.4.5.1.10.1',         # tasa Rx (bps) UBNT-AirMAX-MIB::ubntWlStatRxRate
    'tx': '1.3.6.1.4.1.41112.1.4.5.1.9.1',          # tasa Tx (bps) UBNT-AirMAX-MIB::ubntWlStatTxRate
    'frequency': '1.3.6.1.4.1.41112.1.4.1.1.4.1',   # frecuencia (MHz)
    'ssid': '1.3.6.1.4.1.41112.1.4.5.1.2.1',        # nombre ssid
    'antena': '1.3.6.1.4.1.41112.1.4.1.1.9.1',      # tipo de antena instalada
    #'rssi': '1.3.6.1.4.1.41112.1.4.5.1.6.1',        # UBNT-AirMAX-MIB::ubntWlStatRssi
    #'airmax_q': '1.3.6.1.4.1.41112.1.4.6.1.3.1',    # UBNT-AirMAX-MIB::ubntAirMaxQuality
    #'distancia': '1.3.6.1.4.1.41112.1.4.1.1.7.1',   # UBNT-AirMAX-MIB::ubntRadioDistance (metros)
    #'airmax': '1.3.6.1.4.1.41112.1.4.6.1.4.1',      # UBNT-AirMAX-MIB::ubntAirMaxCapacity.1
}

OIDS_UBNT_AF60 = {
    'memory_p': '1.3.6.1.4.1.41112.1.11.1.2.5.1',     # Memoria %
    'cpu_p': '1.3.6.1.4.1.41112.1.11.1.2.6.1',        # CPU %
    'frequency': '1.3.6.1.4.1.41112.1.11.1.1.2.1',  # UI-AF60-MIB::af60Frequency
    'w_channel': '1.3.6.1.4.1.41112.1.11.1.1.3.1',      # Ancho de canal
    'ssid': '1.3.6.1.4.1.41112.1.11.1.1.4.1',
    'capacity': '1.3.6.1.4.1.41112.1.11.1.3.1.7.36.90.76.244.78.191.1',     # Total Capacity bps
    'tx': '1.3.6.1.4.1.41112.1.11.1.3.1.9.36.90.76.244.78.191.1',           # 60GHz TX Bytes
    'rx': '1.3.6.1.4.1.41112.1.11.1.3.1.10.36.90.76.244.78.191.1',          # 60GHz RX Bytes
    'uptime': '1.3.6.1.4.1.41112.1.11.1.2.7.1',                             # Tiempo de ectividad
    'signal': '1.3.6.1.4.1.41112.1.11.1.3.1.3.36.90.76.244.78.191.1',       # Señal local dbm
    #'ip': '1.3.6.1.4.1.41112.1.11.1.1.5.1',
    #'modelo': '1.3.6.1.4.1.41112.1.11.1.2.3.1',                             # Modelo, largo
    #'signal_r': '1.3.6.1.4.1.41112.1.11.1.3.1.18.36.90.76.244.78.191.1',    # Señal remota dbm
    #'modulacion': '1.3.6.1.4.1.41112.1.11.1.3.1.4.36.90.76.244.78.191.1',   # modulacion de señal
    #'rx_rate': '1.3.6.1.4.1.41112.1.11.1.3.1.5.36.90.76.244.78.191.1',      # RX Data Rate
    #'exp_rx_rate': '1.3.6.1.4.1.41112.1.11.1.3.1.6.36.90.76.244.78.191.1',  # expected RX Data Rate
    #'altitud': '3.6.1.4.1.41112.1.11.1.4.5.1',
}

OIDS_UBNT_AF = {
    'temperatura': '1.3.6.1.4.1.41112.3.2.1.10.1',
    'rx_power0': '1.3.6.1.4.1.41112.3.2.1.11.1',
    'rx_power1': '1.3.6.1.4.1.41112.3.2.1.14.1',
    'enlace': '1.3.6.1.4.1.41112.3.2.1.26.1',
    'eth': '1.3.6.1.4.1.41112.3.2.1.27.1',
    #'uptime': '1.3.6.1.4.1.41112.3.2.1.38.1',
    'firmware': '1.3.6.1.4.1.41112.3.2.1.40.1',
    'distancia': '1.3.6.1.4.1.41112.3.2.1.4.1',
    'capacidad_rx': '1.3.6.1.4.1.41112.3.2.1.5.1',
    'capacidad_tx': '1.3.6.1.4.1.41112.3.2.1.6.1',
    'temp_radio0': '1.3.6.1.4.1.41112.3.2.1.8.1',
    'temp_radio1': '1.3.6.1.4.1.41112.3.2.1.10.1',
}

VENDOR_MAP = {
    'mikrotik': OIDS_MIKROTIK,
    'ubiquiti': OIDS_UBNT_AIRMAX,
    'ubntairmax': OIDS_UBNT_AIRMAX,
    'ubntaf': OIDS_UBNT_AF60,
    'ubntaf60': OIDS_UBNT_AF60,
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