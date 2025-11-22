from django import forms
from .models import ContactosContacto

class ContactoForm(forms.ModelForm):
    class Meta:
        model = ContactosContacto
        fields = [
            'rut_contacto',
            'nombre_contacto',
            'paciente_indice',
            'parentesco',
            'tipo_contacto',
            'fecha_registro',
            'telefono',
            'estado_estudio'
        ]
        widgets = {
            'rut_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-9'
            }),
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del contacto'
            }),
            'paciente_indice': forms.Select(attrs={
                'class': 'form-control'
            }),
            'parentesco': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo_contacto': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_registro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'estado_estudio': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'rut_contacto': 'RUT Contacto',
            'nombre_contacto': 'Nombre Completo',
            'paciente_indice': 'Paciente Índice',
            'parentesco': 'Parentesco',
            'tipo_contacto': 'Tipo de Contacto',
            'fecha_registro': 'Fecha de Registro',
            'telefono': 'Teléfono',
            'estado_estudio': 'Estado del Estudio',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos opcionales
        self.fields['telefono'].required = False
        
        # Si es una instancia existente, hacer el RUT de solo lectura
        if self.instance and self.instance.pk:
            self.fields['rut_contacto'].widget.attrs['readonly'] = True
            self.fields['rut_contacto'].widget.attrs['class'] = 'form-control bg-light'
        else:
            # Establecer fecha actual como valor por defecto para nuevos contactos
            from datetime import date
            self.fields['fecha_registro'].initial = date.today()