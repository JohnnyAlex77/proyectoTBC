# apps/tratamientos/forms.py
from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from apps.pacientes.models import PacientesPaciente as Paciente

class TratamientoForm(forms.ModelForm):
    """
    Formulario para crear y editar tratamientos
    Incluye búsqueda avanzada de pacientes por RUT y validación de tratamiento activo
    """
    
    # Campo para búsqueda por RUT
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
            'paciente': forms.HiddenInput(attrs={'id': 'id_paciente'}),
            'esquema': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'id': 'id_esquema'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
                'id': 'id_fecha_inicio'
            }),
            'fecha_termino_estimada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
                'id': 'id_fecha_termino_estimada'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'required': True,
                'id': 'id_peso_kg'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales del tratamiento...',
                'id': 'id_observaciones'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo paciente no requerido inicialmente
        self.fields['paciente'].required = False
        self.fields['paciente'].label = ""

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino_estimada')
        peso_kg = cleaned_data.get('peso_kg')
        paciente = cleaned_data.get('paciente')
        rut_busqueda = cleaned_data.get('rut_busqueda')

        # Validar que se haya seleccionado un paciente
        if not paciente and not rut_busqueda:
            raise ValidationError({
                'rut_busqueda': 'Debe buscar un paciente por RUT.'
            })
        
        # Si se ingresó un RUT, buscar el paciente
        if rut_busqueda and not paciente:
            paciente_encontrado = self._buscar_paciente_por_rut(rut_busqueda)
            if paciente_encontrado:
                cleaned_data['paciente'] = paciente_encontrado
                # Validar que no tenga tratamiento activo (SOLO para creación)
                if not self.instance.pk:  # Solo validar si es un nuevo tratamiento
                    self._validar_tratamiento_activo(paciente_encontrado)
            else:
                raise ValidationError({
                    'rut_busqueda': f'No se encontró ningún paciente con el RUT: {rut_busqueda}'
                })

        # Si el paciente ya está seleccionado (en edición), también verificar tratamiento activo
        # PERO solo si estamos creando un nuevo tratamiento
        elif paciente and not self.instance.pk:
            self._validar_tratamiento_activo(paciente)

        # Validaciones de fechas y peso
        self._validar_fechas(fecha_inicio, fecha_termino)
        self._validar_peso(peso_kg)
            
        return cleaned_data

    def _buscar_paciente_por_rut(self, rut):
        """Busca paciente por RUT de diferentes formas"""
        rut_limpio = rut.replace('.', '').replace('-', '').upper()
        
        # Búsqueda exacta con formato original
        paciente = Paciente.objects.filter(rut__iexact=rut).first()
        if paciente:
            return paciente
            
        # Búsqueda con RUT limpio
        paciente = Paciente.objects.filter(rut__iexact=rut_limpio).first()
        if paciente:
            return paciente
            
        # Búsqueda manual comparando RUTs limpios
        todos_pacientes = Paciente.objects.all()
        for p in todos_pacientes:
            rut_paciente_limpio = p.rut.replace('.', '').replace('-', '').upper()
            if rut_limpio == rut_paciente_limpio:
                return p
                
        # Búsqueda solo números
        solo_numeros = ''.join(filter(str.isdigit, rut_limpio))
        if solo_numeros:
            for p in todos_pacientes:
                rut_paciente_numeros = ''.join(filter(str.isdigit, p.rut))
                if solo_numeros == rut_paciente_numeros:
                    return p
        return None

    def _validar_tratamiento_activo(self, paciente):
        """Valida que el paciente no tenga tratamiento activo"""
        tratamiento_activo = Tratamiento.objects.filter(
            paciente=paciente,
            resultado_final__in=[None, 'En Tratamiento']
        ).first()
        
        if tratamiento_activo:
            # Usar el método get_esquema_display corregido
            esquema_display = tratamiento_activo.get_esquema_display()
            mensaje_error = f"""
            El paciente {paciente.nombre} ya tiene un tratamiento activo.
            
            Tratamiento # {tratamiento_activo.id}
            - Esquema: {esquema_display}
            - Fecha inicio: {tratamiento_activo.fecha_inicio.strftime('%d/%m/%Y')}
            - Estado: {tratamiento_activo.resultado_final or 'En Tratamiento'}
            
            No se puede crear un nuevo tratamiento hasta que el actual esté finalizado.
            Los tratamientos deben finalizar con: Curación, Tratamiento Completo, Fallecimiento, etc.
            """
            raise ValidationError({
                'rut_busqueda': mensaje_error
            })

    def _validar_fechas(self, fecha_inicio, fecha_termino):
        """Valida las fechas del tratamiento"""
        if fecha_inicio and fecha_termino:
            if fecha_inicio > fecha_termino:
                raise ValidationError({
                    'fecha_termino_estimada': 'La fecha de término no puede ser anterior a la fecha de inicio.'
                })
            if fecha_inicio > date.today():
                raise ValidationError({
                    'fecha_inicio': 'La fecha de inicio no puede ser futura.'
                })

    def _validar_peso(self, peso_kg):
        """Valida el peso del paciente"""
        if peso_kg and peso_kg <= 0:
            raise ValidationError({
                'peso_kg': 'El peso debe ser mayor a 0.'
            })

    def save(self, commit=True):
        """Guardar el tratamiento con validación adicional"""
        # Validación final antes de guardar
        paciente = self.cleaned_data.get('paciente')
        
        if paciente and not self.instance.pk:
            # Verificar una última vez que no exista tratamiento activo
            tratamiento_activo = Tratamiento.objects.filter(
                paciente=paciente,
                resultado_final__in=[None, 'En Tratamiento']
            ).exists()
            
            if tratamiento_activo:
                raise ValidationError({
                    'paciente': 'El paciente ya tiene un tratamiento activo. No se puede crear otro tratamiento.'
                })
        
        return super().save(commit=commit)

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