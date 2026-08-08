from django.db import models


class Sector(models.Model):
    """
    Zona de cobertura o agrupación lógica de dispositivos (ej. 'Sector Norte',
    'Torre Centro'). Útil para organizar el inventario y, más adelante, el mapa.
    """
    nombre = models.CharField(max_length=100, unique=True)
    poblacion = models.CharField(max_length=255, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    altitud = models.IntegerField(default=0, null=True, blank=True, help_text='Altitud en metros sobre el nivel del mar.')

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Dispositivo(models.Model):
    """
    Cualquier equipo de la red: nodo, router, switch, AP, OLT, ONU o antena de cliente.

    Diseño pensado para soportar MikroTik y Ubiquiti (y otras marcas futuras) sin
    forzar campos que no todas comparten: los atributos específicos de cada marca
    o modelo (ej. modo de radio de un AP Ubiquiti, o el tipo de licencia RouterOS)
    se guardan en 'atributos_extra' en vez de crear una columna por cada caso.
    """

    class Tipo(models.TextChoices):
        NODO = 'nodo', 'Nodo'
        ROUTER = 'router', 'Router'
        SWITCH = 'switch', 'Switch'
        AP = 'ap', 'Access Point'
        ST = 'stp', 'Estación'
        OLT = 'olt', 'OLT'
        ONU = 'onu', 'ONU'
        ANTENA_CLIENTE = 'antena_cliente', 'Antena de cliente',
        OTROS = 'otros', 'Otros'

    class Marca(models.TextChoices):
        MIKROTIK = 'mikrotik', 'MikroTik'
        UBIQUITI = 'ubiquiti', 'Ubiquiti'
        DLINK = 'dlink', 'D-Link'
        TPLINK = 'tplink', 'TP-Link'
        HUAWEI = 'huawei', 'Huawei'
        TENDA = 'tenda', 'Tenda'
        ASUS = 'asus', 'Asus'
        NETGEAR = 'netgear', 'Netgear'
        CISCO = 'cisco', 'Cisco'
        ZTE = 'zte', 'ZTE'
        HPE = 'hpe', 'HPE Aruba'
        FORTINET = 'fortinet', 'Fortinet'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'
        MANTENIMIENTO = 'mantenimiento', 'En mantenimiento',
        INSTALACION = 'instalacion', 'En instalación'

    class Rol(models.TextChoices):
        MAIN = 'main', 'Principal'
        STATION = 'station', 'Estación'
        MASTER = 'master', 'Master'
        SLAVE = 'slave', 'Esclavo'
        OTRO = 'otro', 'Otro'
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    marca = models.CharField(max_length=20, choices=Marca.choices)
    modelo = models.CharField(max_length=100, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.OTRO, verbose_name='Modo operación')

    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispositivos')
    cliente = models.ForeignKey(
        'clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dispositivos',
        help_text='Solo aplica cuando el tipo es "Antena de cliente".',
    )

    ip_gestion = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de gestión')
    mac_address = models.CharField(max_length=17, blank=True, verbose_name='Dirección MAC')
    firmware_version = models.CharField(max_length=50, blank=True)

    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    fecha_instalacion = models.DateField(null=True, blank=True)

    atributos_extra = models.JSONField(
        default=dict, blank=True,
        verbose_name='Atributos adicionales',
        help_text='Datos específicos de la marca/modelo que no aplican a todos los dispositivos.',
    )
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()} · {self.get_marca_display()})'


class Interfaz(models.Model):
    """Interfaz de red de un dispositivo (puerto físico, radio, VLAN, etc.)."""

    class Tipo(models.TextChoices):
        ETHERNET = 'ethernet', 'Ethernet'
        WIRELESS = 'wireless', 'Inalámbrica'
        PPPOE = 'pppoe', 'PPPoE'
        VLAN = 'vlan', 'VLAN'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        ARRIBA = 'arriba', 'Arriba'
        ABAJO = 'abajo', 'Abajo'
        DESCONOCIDO = 'desconocido', 'Desconocido'

    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='interfaces')
    nombre = models.CharField(max_length=100, help_text="Ej. 'ether1', 'wlan0', 'vlan100'")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.ETHERNET)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.DESCONOCIDO)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    vlan_id = models.PositiveIntegerField(null=True, blank=True)
    velocidad_mbps = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Interfaz'
        verbose_name_plural = 'Interfaces'
        unique_together = ('dispositivo', 'nombre')
        ordering = ['dispositivo', 'nombre']

    def __str__(self):
        return f'{self.dispositivo.nombre} · {self.nombre}'


class Enlace(models.Model):
    """
    Conexión lógica entre dos dispositivos (backbone, acceso o radioenlace).
    Sirve como base para, más adelante, dibujar el mapa de topología de red.
    """

    class Tipo(models.TextChoices):
        BACKBONE = 'backbone', 'Backbone'
        ACCESO = 'acceso', 'Acceso'
        RADIOENLACE = 'radioenlace', 'Radioenlace',
        TORNCAL = 'torncal', 'Torncal'

    dispositivo_origen = models.ForeignKey(
        Dispositivo, on_delete=models.CASCADE, related_name='enlaces_origen',
    )
    dispositivo_destino = models.ForeignKey(
        Dispositivo, on_delete=models.CASCADE, related_name='enlaces_destino',
    )
    interfaz_origen = models.ForeignKey(
        Interfaz, on_delete=models.SET_NULL, null=True, blank=True, related_name='enlaces_como_origen',
    )
    interfaz_destino = models.ForeignKey(
        Interfaz, on_delete=models.SET_NULL, null=True, blank=True, related_name='enlaces_como_destino',
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.ACCESO)
    ancho_banda_mbps = models.PositiveIntegerField(null=True, blank=True)
    distancia_km = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    frecuencia_ghz = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True,
        help_text='Solo aplica a radioenlaces.',
    )
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Enlace'
        verbose_name_plural = 'Enlaces'

    def __str__(self):
        return f'{self.dispositivo_origen.nombre} → {self.dispositivo_destino.nombre}'
