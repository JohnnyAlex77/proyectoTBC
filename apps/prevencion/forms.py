from django import forms
from .models import PrevencionQuimioprofilaxis, PrevencionVacunacionBCG, PrevencionSeguimiento
from apps.pacientes.models import PacientesPaciente
from apps.contactos.models import ContactosContacto

class QuimioprofilaxisForm(forms.ModelForm):
    class Meta:
        model = PrevencionQuimioprofilaxis
        fields = [
            'tipo_paciente', 'paciente', 'contacto', 'medicamento', 'dosis',
            'fecha_inicio', 'fecha_termino_prevista', 'fecha_termino_real', 'esquema',
            'estado', 'adherencia_porcentaje', 'efectos_adversos', 'observaciones'
        ]
        widgets = {
            'tipo_paciente': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_paciente'}),
            'paciente': forms.Select(attrs={'class': 'form-select', 'id': 'id_paciente'}),
            'contacto': forms.Select(attrs={'class': 'form-select', 'id': 'id_contacto'}),
            'medicamento': forms.Select(attrs={'class': 'form-select'}),
            'dosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300mg diarios'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_termino_prevista': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_termino_real': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'esquema': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 6H - 6 meses de Isoniacida'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'adherencia_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'efectos_adversos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa cualquier efecto adverso presentado...'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].required = False
        self.fields['contacto'].required = False
        
        # Filtrar pacientes activos
        self.fields['paciente'].queryset = PacientesPaciente.objects.filter(estado='activo')
        
        # Filtrar contactos
        self.fields['contacto'].queryset = ContactosContacto.objects.all()
        
        # Formatear fechas para que se muestren en los inputs
        if self.instance and self.instance.pk:
            if self.instance.fecha_inicio:
                self.initial['fecha_inicio'] = self.instance.fecha_inicio.strftime('%Y-%m-%d')
            if self.instance.fecha_termino_prevista:
                self.initial['fecha_termino_prevista'] = self.instance.fecha_termino_prevista.strftime('%Y-%m-%d')
            if self.instance.fecha_termino_real:
                self.initial['fecha_termino_real'] = self.instance.fecha_termino_real.strftime('%Y-%m-%d')

class VacunacionBCGForm(forms.ModelForm):
    class Meta:
        model = PrevencionVacunacionBCG
        fields = [
            'paciente', 'fecha_vacunacion', 'lote', 'establecimiento',
            'reaccion', 'observaciones_reaccion'
        ]
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'fecha_vacunacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'establecimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'reaccion': forms.Select(attrs={'class': 'form-select'}),
            'observaciones_reaccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar pacientes activos
        self.fields['paciente'].queryset = PacientesPaciente.objects.filter(estado='activo')
        
        if self.instance and self.instance.pk and self.instance.fecha_vacunacion:
            self.initial['fecha_vacunacion'] = self.instance.fecha_vacunacion.strftime('%Y-%m-%d')

class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = PrevencionSeguimiento
        fields = [
            'tipo_seguimiento', 'quimioprofilaxis', 'vacunacion',
            'fecha_seguimiento', 'resultado', 'observaciones', 'proximo_control'
        ]
        widgets = {
            'tipo_seguimiento': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_seguimiento'}),
            'quimioprofilaxis': forms.Select(attrs={'class': 'form-select', 'id': 'id_quimioprofilaxis'}),
            'vacunacion': forms.Select(attrs={'class': 'form-select', 'id': 'id_vacunacion'}),
            'fecha_seguimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'proximo_control': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['quimioprofilaxis'].required = False
        self.fields['vacunacion'].required = False
        
        # Filtrar quimioprofilaxis activas
        self.fields['quimioprofilaxis'].queryset = PrevencionQuimioprofilaxis.objects.filter(estado='en_curso')
        
        # Filtrar vacunaciones
        self.fields['vacunacion'].queryset = PrevencionVacunacionBCG.objects.all()
        
        # Pre-seleccionar quimioprofilaxis si viene por URL
        if self.request:
            quimioprofilaxis_id = self.request.GET.get('quimioprofilaxis')
            if quimioprofilaxis_id:
                self.fields['quimioprofilaxis'].initial = quimioprofilaxis_id
                self.fields['tipo_seguimiento'].initial = 'quimioprofilaxis'