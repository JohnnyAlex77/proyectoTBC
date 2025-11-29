from django import forms
from .models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from apps.pacientes.models import PacientesPaciente as Paciente
from django.core.exceptions import ValidationError
from datetime import date

class TratamientoForm(forms.ModelForm):
    # Campo adicional para búsqueda por RUT
    rut_busqueda = forms.CharField(
        max_length=15,
        required=False,
        label='Buscar paciente por RUT',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese RUT del paciente (ej: 12345678-9)',
            'id': 'rut_busqueda'
        })
    )
    
    class Meta:
        model = Tratamiento
        fields = ['paciente', 'esquema', 'fecha_inicio', 'fecha_termino_estimada', 'peso_kg', 'observaciones']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'id': 'id_paciente'
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
        
        # Inicialmente no mostrar pacientes en el select, se cargarán vía búsqueda
        self.fields['paciente'].queryset = Paciente.objects.none()
        
        # Mejorar etiquetas
        self.fields['paciente'].label = "Paciente seleccionado"
        self.fields['fecha_inicio'].label = "Fecha de Inicio del Tratamiento"
        self.fields['fecha_termino_estimada'].label = "Fecha de Término Estimada"
        
        # Hacer el campo paciente no requerido inicialmente (se validará después)
        self.fields['paciente'].required = False

    def clean(self):
        """
        Validación personalizada del formulario
        """
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino_estimada')
        peso_kg = cleaned_data.get('peso_kg')
        paciente = cleaned_data.get('paciente')
        rut_busqueda = cleaned_data.get('rut_busqueda')

        # Validar que se haya seleccionado un paciente o se haya buscado por RUT
        if not paciente and not rut_busqueda:
            raise ValidationError({
                'rut_busqueda': 'Debe buscar un paciente por RUT o seleccionar uno de la lista.'
            })
        
        # Si se ingresó un RUT, buscar el paciente
        if rut_busqueda and not paciente:
            try:
                # Limpiar el RUT (eliminar puntos y guión)
                rut_limpio = rut_busqueda.replace('.', '').replace('-', '').upper()
                paciente_encontrado = Paciente.objects.get(rut__icontains=rut_limpio)
                cleaned_data['paciente'] = paciente_encontrado
                
                # Verificar si el paciente ya tiene un tratamiento activo
                tratamiento_activo = Tratamiento.objects.filter(
                    paciente=paciente_encontrado,
                    resultado_final__in=[None, 'En Tratamiento']
                ).exists()
                
                if tratamiento_activo:
                    raise ValidationError({
                        'rut_busqueda': f'El paciente {paciente_encontrado.nombre} ya tiene un tratamiento activo.'
                    })
                    
            except Paciente.DoesNotExist:
                raise ValidationError({
                    'rut_busqueda': 'No se encontró ningún paciente con el RUT ingresado.'
                })
            except Paciente.MultipleObjectsReturned:
                raise ValidationError({
                    'rut_busqueda': 'Se encontraron múltiples pacientes con el RUT ingresado. Contacte al administrador.'
                })

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
        """
        Validación del esquema de medicamento
        """
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino')

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
        """
        Inicializar el formulario con valores por defecto
        """
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