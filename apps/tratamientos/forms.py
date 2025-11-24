from django import forms
from .models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from apps.pacientes.models import PacientesPaciente as Paciente
from django.core.exceptions import ValidationError
from datetime import date

class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['paciente', 'esquema', 'fecha_inicio', 'fecha_termino_estimada', 'peso_kg', 'observaciones']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'esquema': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'fecha_termino_estimada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'required': True
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales del tratamiento...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: Usar los mismos estados que en el modelo Paciente
        pacientes_activos = Paciente.objects.filter(
            estado__in=['activo', 'Activo', 'Activo en tratamiento']
        ).order_by('nombre')
        
        self.fields['paciente'].queryset = pacientes_activos
        
        # Mejorar etiquetas
        self.fields['paciente'].label = "Seleccionar Paciente"
        self.fields['fecha_inicio'].label = "Fecha de Inicio del Tratamiento"
        self.fields['fecha_termino_estimada'].label = "Fecha de Término Estimada"
        
        # Personalizar la representación de los pacientes
        self.fields['paciente'].label_from_instance = lambda obj: f"{obj.nombre} - {obj.rut}"

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino_estimada')
        peso_kg = cleaned_data.get('peso_kg')

        # Validar fechas
        if fecha_inicio and fecha_termino:
            if fecha_inicio > fecha_termino:
                raise ValidationError({
                    'fecha_termino_estimada': 'La fecha de término no puede ser anterior a la fecha de inicio.'
                })
            if fecha_inicio > date.today():
                raise ValidationError({
                    'fecha_inicio': 'La fecha de inicio no puede ser futura.'
                })
        # Validar peso
        if peso_kg and peso_kg <= 0:
            raise ValidationError({
                'peso_kg': 'El peso debe ser mayor a 0.'
            })
        return cleaned_data

class EsquemaMedicamentoForm(forms.ModelForm):
    class Meta:
        model = EsquemaMedicamento
        fields = ['medicamento', 'dosis_mg', 'frecuencia', 'fase', 'duracion_semanas', 'fecha_inicio', 'fecha_termino']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control'}),
            'dosis_mg': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '50'
            }),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'fase': forms.Select(attrs={'class': 'form-control'}),
            'duracion_semanas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '104'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_termino': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino')
        duracion_semanas = cleaned_data.get('duracion_semanas')

        if fecha_inicio and fecha_termino and fecha_inicio > fecha_termino:
            raise ValidationError('La fecha de término no puede ser anterior a la fecha de inicio.')

        return cleaned_data

class DosisAdministradaForm(forms.ModelForm):
    class Meta:
        model = DosisAdministrada
        fields = ['fecha_dosis', 'administrada', 'hora_administracion', 'observaciones']
        widgets = {
            'fecha_dosis': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_administracion': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones sobre la administración...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_dosis'].initial = date.today()

class TratamientoUpdateForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['esquema', 'fecha_termino_real', 'peso_kg', 'resultado_final', 'observaciones']
        widgets = {
            'esquema': forms.Select(attrs={'class': 'form-control'}),
            'fecha_termino_real': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'resultado_final': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }