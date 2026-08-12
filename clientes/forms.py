from django import forms
from .models import Cliente, Contrato


class BootstrapFormMixin:
    """Agrega automáticamente las clases de Bootstrap a cada campo, para no
    tener que repetirlas a mano en cada formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                css_extra = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_extra = 'form-select'
            else:
                css_extra = 'form-control'
            actual = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{actual} {css_extra}'.strip()


class ClienteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre_completo', 'apodo', 'tipo_documento', 'numero_documento',
            'telefono', 'telefono_alternativo', 'email', 'poblacion', 'direccion',
            'latitud', 'longitud', 'activo', 'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }


class ContratoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Contrato
        fields = [
            'nombre', 'plan', 'precio_mensual', 'estado', 'fecha_inicio', 'fecha_cancelacion',
            'conexion', 'identificador_mikrotik', 'pppoe_clave', 'ip_asignada', 'notas',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_cancelacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'conexion': forms.Select(attrs={'x-on:change': 'conexion = $event.target.value'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
