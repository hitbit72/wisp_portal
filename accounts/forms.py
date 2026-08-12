from django import forms
from .models import Usuario


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

class LoginForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }
