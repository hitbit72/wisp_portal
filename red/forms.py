from django import forms

from clientes.forms import BootstrapFormMixin

from .models import Dispositivo, Enlace, Interfaz, Sector


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

    class Meta:
        model = Dispositivo
        fields = [
            'nombre', 'tipo', 'marca', 'modelo', 'cliente',
            'ip_gestion', 'mac_address', 'firmware_version',
            'estado', 'fecha_instalacion', 'latitud', 'longitud', 'atributos_extra', 'notas',
        ]
        widgets = {
            'fecha_instalacion': forms.DateInput(attrs={'type': 'date'}),
            'atributos_extra': forms.Textarea(attrs={'rows': 5}),
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
    origen se restringe a las del dispositivo origen."""

    def __init__(self, *args, dispositivo_origen=None, **kwargs):
        super().__init__(*args, **kwargs)
        if dispositivo_origen is not None:
            self.fields['interfaz_origen'].queryset = dispositivo_origen.interfaces.all()

    class Meta:
        model = Enlace
        fields = [
            'dispositivo_destino', 'interfaz_origen', 'interfaz_destino',
            'tipo', 'ancho_banda_mbps', 'distancia_km', 'frecuencia_ghz', 'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }