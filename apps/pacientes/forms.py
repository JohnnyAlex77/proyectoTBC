from django import forms
from .models import PacientesPaciente

class PacienteForm(forms.ModelForm):
    # Campos adicionales para el formulario (no se guardan en el modelo directamente)
    nueva_enfermedad = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una enfermedad preexistente',
            'id': 'nueva-enfermedad'
        }),
        label="Agregar enfermedad"
    )
    
    nueva_alergia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una alergia',
            'id': 'nueva-alergia'
        }),
        label="Agregar alergia"
    )

    class Meta:
        model = PacientesPaciente
        fields = [
            'rut', 'nombre', 'fecha_nacimiento', 'sexo', 'domicilio',
            'comuna', 'telefono', 'establecimiento_salud', 'fecha_diagnostico',
            'tipo_tbc', 'baciloscopia_inicial', 'cultivo_inicial',
            'poblacion_prioritaria', 'estado', 'enfermedades_preexistentes', 'alergias'
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
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
            }),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'domicilio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
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
            'fecha_diagnostico': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={
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
            'enfermedades_preexistentes': forms.HiddenInput(attrs={'id': 'enfermedades-input'}),
            'alergias': forms.HiddenInput(attrs={'id': 'alergias-input'}),
        }
        labels = {
            'rut': 'RUT',
            'nombre': 'Nombre Completo',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'sexo': 'Sexo',
            'domicilio': 'Domicilio',
            'comuna': 'Comuna',
            'telefono': 'Teléfono',
            'establecimiento_salud': 'Establecimiento de Salud',
            'fecha_diagnostico': 'Fecha de Diagnóstico',
            'tipo_tbc': 'Tipo de TBC',
            'baciloscopia_inicial': 'Baciloscopia Inicial',
            'cultivo_inicial': 'Cultivo Inicial',
            'poblacion_prioritaria': 'Población Prioritaria',
            'estado': 'Estado del Paciente',
            'enfermedades_preexistentes': 'Enfermedades Preexistentes',
            'alergias': 'Alergias',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['poblacion_prioritaria'].required = False
        self.fields['baciloscopia_inicial'].required = False
        self.fields['cultivo_inicial'].required = False
        self.fields['fecha_diagnostico'].required = False
        self.fields['enfermedades_preexistentes'].required = False
        self.fields['alergias'].required = False

        # Agregar opciones para población prioritaria
        self.fields['poblacion_prioritaria'].choices = [
            ('', 'Seleccione una opción'),
            ('migrante', 'Población Migrante'),
            ('indígena', 'Pueblos Originarios'),
            ('privada_libertad', 'Privada de Libertad'),
            ('sin_techo', 'Personas en Situación de Calle'),
            ('vih', 'Personas con VIH'),
            ('diabetes', 'Personas con Diabetes'),
            ('desnutricion', 'Personas con Desnutrición'),
            ('alcoholismo', 'Personas con Alcoholismo'),
            ('tabaquismo', 'Personas con Tabaquismo'),
            ('otra', 'Otra Población Prioritaria'),
        ]

        # Configurar el formato de fecha para los campos de fecha
        if self.instance and self.instance.pk:
            if self.instance.fecha_nacimiento:
                self.fields['fecha_nacimiento'].widget.attrs['value'] = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')
            if self.instance.fecha_diagnostico:
                self.fields['fecha_diagnostico'].widget.attrs['value'] = self.instance.fecha_diagnostico.strftime('%Y-%m-%d')