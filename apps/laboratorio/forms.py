from django import forms
from .models import LaboratorioRedLaboratorios, LaboratorioControlCalidad, LaboratorioTarjetero, LaboratorioIndicadores

class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = LaboratorioRedLaboratorios
        fields = '__all__'
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@laboratorio.cl'}),
        }
        labels = {
            'activo': 'Laboratorio activo',
        }

class ControlCalidadForm(forms.ModelForm):
    class Meta:
        model = LaboratorioControlCalidad
        fields = ['laboratorio', 'fecha_control', 'tipo_control', 'resultado', 'observaciones']
        widgets = {
            'fecha_control': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describa los resultados del control de calidad...'}),
        }

class TarjeteroForm(forms.ModelForm):
    class Meta:
        model = LaboratorioTarjetero
        fields = ['paciente', 'examen', 'fecha_deteccion', 'tipo_muestra', 'resultado', 'laboratorio_referencia', 'fecha_notificacion']
        widgets = {
            'fecha_deteccion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_notificacion': forms.DateInput(attrs={'type': 'date'}),
            'resultado': forms.TextInput(attrs={'placeholder': 'Ej: BK+, GeneXpert positivo, etc.'}),
        }

class IndicadoresForm(forms.ModelForm):
    class Meta:
        model = LaboratorioIndicadores
        fields = ['laboratorio', 'periodo', 'muestras_recibidas', 'muestras_procesadas', 'positivos', 'contaminacion_porcentaje', 'tiempo_respuesta_promedio']
        widgets = {
            'periodo': forms.TextInput(attrs={'placeholder': 'YYYY-MM', 'pattern': '\\d{4}-\\d{2}'}),
            'contaminacion_porcentaje': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'tiempo_respuesta_promedio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        help_texts = {
            'periodo': 'Formato: AAAA-MM (ej: 2024-01)',
            'contaminacion_porcentaje': 'Porcentaje de muestras contaminadas',
            'tiempo_respuesta_promedio': 'Tiempo promedio en horas para entrega de resultados',
        }