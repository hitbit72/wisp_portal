from django import forms
from django.urls import reverse

from clientes.forms import BootstrapFormMixin

from .models import Dispositivo, Enlace, Interfaz, Sector


def _etiqueta_dispositivo(obj):
    """Etiqueta del selector de dispositivo destino: 'nombre (tipo · IP · sector)'."""
    ip = obj.ip_gestion or 'sin IP'
    sector = obj.sector.nombre if obj.sector_id else 'Sin sector'
    return f'{obj.nombre} ({obj.get_tipo_display()} · {ip} · {sector})'


def _etiqueta_interfaz(obj):
    """Etiqueta de interfaz: solo el nombre, para que coincida con las
    opciones que se cargan dinámicamente por dispositivo."""
    return obj.nombre


class JSONTextoOpcional(forms.JSONField):
    """
    Campo JSON tolerante: si el texto introducido es JSON válido se guarda
    como dict/list; si no, se guarda el texto tal cual (como string) en vez
    de rechazar el formulario. Así un usuario no pierde el formulario por
    escribir un formato suelto (p.ej. 'modelo: lhg').
    """

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, (list, dict, int, float)):
            return value
        if isinstance(value, str) and not value.strip():
            return None
        try:
            return super().to_python(value)
        except forms.ValidationError:
            return value.strip()


class SectorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Sector
        fields = [
            'nombre', 'poblacion', 'direccion', 'descripcion',
            'latitud', 'longitud', 'altitud',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class DispositivoForm(BootstrapFormMixin, forms.ModelForm):
    """'sector' no se edita desde el formulario: se fija desde la vista
    al crear un dispositivo bajo un sector concreto."""

    atributos_extra = JSONTextoOpcional(
        required=False,
        label='Atributos del dispositivo',
        help_text='Datos específicos de la marca/modelo. Puedes escribir texto suelto o un objeto JSON válido (p.ej. {"banda": 5}).',
        widget=forms.Textarea(attrs={'rows': 5}),
    )

    class Meta:
        model = Dispositivo
        fields = [
            'nombre', 'rol', 'tipo', 'marca', 'modelo', 'cliente',
            'ip_gestion', 'mac_address', 'firmware_version',
            'estado', 'fecha_instalacion', 'latitud', 'longitud', 'atributos_extra', 'notas',
        ]
        widgets = {
            'fecha_instalacion': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }


class InterfazForm(BootstrapFormMixin, forms.ModelForm):
    """'dispositivo' se fija desde la vista."""

    class Meta:
        model = Interfaz
        fields = [
            'nombre', 'tipo', 'estado', 'ip_address', 'mac_address',
            'vlan_id', 'velocidad_mbps',
        ]


class EnlaceForm(BootstrapFormMixin, forms.ModelForm):
    """'dispositivo_origen' se fija desde la vista; la lista de interfaces
    origen se restringe a las del dispositivo origen. El destino se etiqueta
    con 'nombre (tipo · IP · sector)' y sus interfaces se cargan dinámicamente
    vía HTMX al cambiar el dispositivo destino."""

    def __init__(self, *args, dispositivo_origen=None, **kwargs):
        super().__init__(*args, **kwargs)
        if dispositivo_origen is not None:
            self.fields['interfaz_origen'].queryset = dispositivo_origen.interfaces.all()

        destino = self.fields['dispositivo_destino']
        destino.queryset = Dispositivo.objects.select_related('sector')
        destino.label_from_instance = _etiqueta_dispositivo
        destino.widget.attrs.update({
            'hx-get': reverse('red:opciones_interfaces_dispositivo'),
            'hx-trigger': 'change',
            'hx-target': '#id_interfaz_destino',
            'hx-swap': 'innerHTML',
            'hx-include': '#id_dispositivo_destino',
        })

        self.fields['interfaz_destino'].label_from_instance = _etiqueta_interfaz

        if self.is_bound:
            destino_id = self.data.get('dispositivo_destino')
            if destino_id:
                self.fields['interfaz_destino'].queryset = Interfaz.objects.filter(
                    dispositivo_id=destino_id
                )
        elif self.instance and self.instance.dispositivo_destino_id:
            self.fields['interfaz_destino'].queryset = self.instance.dispositivo_destino.interfaces.all()

    class Meta:
        model = Enlace
        fields = [
            'dispositivo_destino', 'interfaz_origen', 'interfaz_destino',
            'tipo', 'ancho_banda_mbps', 'distancia_km', 'frecuencia_ghz', 'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }