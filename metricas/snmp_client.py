"""
Cliente SNMP del servicio de monitorización (pysnmp-lextudio).

Expone helpers simples sobre la API clásica síncrona de pysnmp:
- `consultar_escalares(dispositivo, oids)`: GET múltiple de OIDs escalares.
- `consultar_if_table(dispositivo)`: estado de interfaces (ifTable, walk).

El transporte se configura por dispositivo desde
`Dispositivo.atributos_extra['snmp']` (puerto, timeout, reintentos), con los
valores por defecto de `settings.METRICAS_SNMP`.
"""

import django.conf as _conf

from pysnmp.hlapi import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    getCmd,
    nextCmd,
)

MODO_IPV4 = 0  # CommunityData(mpModel=0) -> SNMPv2c

OID_IF_DESCR = '1.3.6.1.2.1.2.2.1.2'
OID_IF_OPER = '1.3.6.1.2.1.2.2.1.8'


class SnmpError(Exception):
    """Error de consulta SNMP (sin respuesta, protocolo, etc.)."""


def _objetos(oid):
    return ObjectType(ObjectIdentity(oid))


def _valor_numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        try:
            return float(str(valor))
        except ValueError:
            return None


def _valor_texto(valor):
    try:
        texto = str(valor.prettyPrint())
    except AttributeError:
        texto = str(valor)
    if texto.startswith('No Such Object') or texto.startswith('No Such Instance'):
        return ''
    return texto


def _conf_snmp(dispositivo):
    conf = dict(_conf.settings.METRICAS_SNMP)
    snmp = (dispositivo.atributos_extra or {}).get('snmp') or {}
    conf.update(snmp)
    return conf


def _trasporte(host, conf):
    return UdpTransportTarget(
        (host, int(conf['puerto'])),
        timeout=float(conf['timeout']),
        retries=int(conf['reintentos']),
    )


def _auth(comunidad):
    return CommunityData(comunidad, mpModel=MODO_IPV4)


def consultar_escalares(dispositivo, oids):
    """GET múltiple: dict métrica -> OID. Devuelve dict métrica ->
    (valor_numero, valor_texto). Los OIDs sin soporte se omiten. Lanza
    SnmpError si el equipo no responde o da error de protocolo."""
    if not oids:
        return {}
    conf = _conf_snmp(dispositivo)
    comunidad = dispositivo.snmp_community or 'public'
    objetos = [_objetos(oid) for oid in oids.values()]

    error_ind, error_st, _, var_binds = next(
        getCmd(
            SnmpEngine(),
            _auth(comunidad),
            _trasporte(dispositivo.ip_gestion, conf),
            ContextData(),
            *objetos,
        )
    )
    if error_ind:
        raise SnmpError(str(error_ind))
    if error_st:
        raise SnmpError(error_st.prettyPrint())

    resultado = {}
    for (oid, valor), metrica in zip(var_binds, oids):
        texto = _valor_texto(valor)
        if not texto:
            continue
        resultado[metrica] = (_valor_numero(valor), texto)
    return resultado


def consultar_if_table(dispositivo):
    """Walk de ifTable (descr + oper status). Devuelve lista de
    {nombre, estado} con estado 'up'/'down'."""
    conf = _conf_snmp(dispositivo)
    comunidad = dispositivo.snmp_community or 'public'
    engine = SnmpEngine()
    transporte = _trasporte(dispositivo.ip_gestion, conf)
    contexto = ContextData()

    descr, oper = {}, {}
    for columna, bucket in ((OID_IF_DESCR, descr), (OID_IF_OPER, oper)):
        iterador = nextCmd(
            engine, _auth(comunidad), transporte, contexto, _objetos(columna),
        )
        try:
            while True:
                error_ind, error_st, _, var_binds = next(iterador)
                if error_ind:
                    raise SnmpError(str(error_ind))
                if error_st:
                    raise SnmpError(error_st.prettyPrint())
                for oid, valor in var_binds:
                    bucket[str(oid)] = _valor_texto(valor)
        except StopIteration:
            pass

    puertos = []
    for sufijo in sorted(set(descr) | set(oper)):
        nombre = descr.get(sufijo) or f'if {sufijo.rsplit(".", 1)[-1]}'
        oper_raw = oper.get(sufijo, '2')
        puertos.append({
            'nombre': nombre,
            'estado': 'up' if oper_raw == '1' else 'down',
        })
    return puertos
