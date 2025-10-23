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
            'parentesco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Hijo/a, Esposo/a, Padre, etc.'
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar labels si es necesario
        self.fields['paciente_indice'].label = "Paciente Índice"
        self.fields['rut_contacto'].label = "RUT Contacto"
        self.fields['nombre_contacto'].label = "Nombre Contacto"
        self.fields['estado_estudio'].label = "Estado del Estudio"