# apps/pacientes/forms.py
from django import forms
from .models import PacientesPaciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = PacientesPaciente
        fields = [
            'rut', 'nombre', 'fecha_nacimiento', 'sexo', 'domicilio', 
            'comuna', 'telefono', 'establecimiento_salud', 'fecha_diagnostico',
            'tipo_tbc', 'baciloscopia_inicial', 'cultivo_inicial', 
            'poblacion_prioritaria', 'estado'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '12.345.678-9'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del paciente'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'domicilio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'comuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comuna de residencia'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'establecimiento_salud': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Centro de salud de atención'
            }),
            'fecha_diagnostico': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'tipo_tbc': forms.Select(attrs={'class': 'form-control'}),
            'baciloscopia_inicial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Positivo 2+'
            }),
            'cultivo_inicial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Mycobacterium tuberculosis'
            }),
            'poblacion_prioritaria': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'rut': 'RUT',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'fecha_diagnostico': 'Fecha de Diagnóstico',
            'tipo_tbc': 'Tipo de TBC',
            'baciloscopia_inicial': 'Baciloscopía Inicial',
            'cultivo_inicial': 'Cultivo Inicial',
            'poblacion_prioritaria': 'Población Prioritaria',
            'establecimiento_salud': 'Establecimiento de Salud',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo poblacion_prioritario opcional
        self.fields['poblacion_prioritaria'].required = False
        self.fields['baciloscopia_inicial'].required = False
        self.fields['cultivo_inicial'].required = False