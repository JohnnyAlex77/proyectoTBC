# apps/examenes/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ExamenesExamenbacteriologico
from apps.pacientes.models import PacientesPaciente

class ExamenBacteriologicoForm(forms.ModelForm):
    # Campos para búsqueda de paciente por RUT
    rut_busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese RUT del paciente',
            'id': 'rut_busqueda'
        }),
        label="Buscar Paciente por RUT"
    )
    
    # Campo para búsqueda de laboratorio
    laboratorio_busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar laboratorio por nombre',
            'id': 'laboratorio_busqueda'
        }),
        label="Buscar Laboratorio"
    )

    # Campos ocultos para IDs
    paciente_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'paciente_id'})
    )

    paciente_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'paciente_display',
            'placeholder': 'Seleccione un paciente usando el buscador de RUT'
        }),
        label="Paciente Seleccionado"
    )

    laboratorio_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly', 
            'id': 'laboratorio_display',
            'placeholder': 'Seleccione un laboratorio usando el buscador'
        }),
        label="Laboratorio Seleccionado"
    )

    fecha_solicitud = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Solicitud",
    )
    
    fecha_toma_muestra = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Toma de Muestra"
    )
    
    fecha_ingreso_laboratorio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha Ingreso Laboratorio"
    )
    
    fecha_resultado = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha Resultado"
    )

    tipo_examen = forms.ChoiceField(
        choices=ExamenesExamenbacteriologico.TIPO_EXAMEN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Examen"
    )
    
    tipo_muestra = forms.ChoiceField(
        choices=ExamenesExamenbacteriologico.TIPO_MUESTRA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Muestra"
    )
    
    sensibilidad = forms.ChoiceField(
        choices=ExamenesExamenbacteriologico.SENSIBILIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Sensibilidad"
    )
    
    # Campo para usuario que tomó la muestra como CharField
    usuario_toma_muestra_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del usuario que tomó la muestra'
        }),
        label="Usuario que tomó la muestra"
    )

    class Meta:
        model = ExamenesExamenbacteriologico
        fields = [
            'paciente', 'tipo_examen', 'tipo_muestra', 'otro_tipo_muestra',
            'fecha_solicitud', 'fecha_toma_muestra', 'fecha_ingreso_laboratorio',
            'fecha_resultado', 'resultado', 'resultado_cuantitativo',
            'resultado_cualitativo', 'sensibilidad', 'resistencia_isoniazida',
            'resistencia_rifampicina', 'resistencia_pirazinamida',
            'resistencia_etambutol', 'resistencia_estreptomicina',
            'resistencia_fluoroquinolonas', 'observaciones_muestra',
            'observaciones_resultado', 'prioridad', 'laboratorio',
            'numero_muestra_lab', 'usuario_toma_muestra'
        ]
        
        widgets = {
            'paciente': forms.HiddenInput(),  # Ocultar el campo original
            'otro_tipo_muestra': forms.TextInput(attrs={ 
                'class': 'form-control',
                'placeholder': 'Especificar tipo de muestra'
            }),
            'resultado': forms.Select(attrs={'class': 'form-select'}),
            'resultado_cuantitativo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2+, 3+, escaso, moderado, abundante'
            }),
            'resultado_cualitativo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del resultado'
            }),
            'observaciones_muestra': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre la muestra'
            }),
            'observaciones_resultado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre el resultado'
            }),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'numero_muestra_lab': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de muestra asignado por el laboratorio'
            }),
            'laboratorio': forms.HiddenInput(),  # Ocultar el campo original
            'usuario_toma_muestra': forms.HiddenInput(),  # Ocultar el campo original
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Ocultar campos originales que manejaremos con lógica personalizada
        self.fields['paciente'].widget = forms.HiddenInput()
        self.fields['laboratorio'].widget = forms.HiddenInput(attrs={'id': 'id_laboratorio'})
        self.fields['usuario_toma_muestra'].widget = forms.HiddenInput()
        
        # Establecer fecha_solicitud por defecto para nuevos registros
        if not self.instance.pk:
            self.fields['fecha_solicitud'].initial = timezone.now().date()
        
        # Si estamos editando, cargar datos del paciente y laboratorio
        if self.instance.pk:
            # Cargar datos del paciente
            if self.instance.paciente:
                self.initial['paciente_id'] = self.instance.paciente.pk
                # Usar campos reales del modelo PacientesPaciente
                paciente_nombre = self.instance.paciente.nombre
                paciente_rut = self.instance.paciente.rut
                display_text = f"{paciente_nombre} - {paciente_rut}"
                self.initial['paciente_display'] = display_text
            
            # Cargar datos del laboratorio
            if self.instance.laboratorio:
                self.initial['laboratorio_display'] = self.instance.laboratorio
            
            # Cargar datos del usuario que tomó la muestra
            if self.instance.usuario_toma_muestra:
                usuario_nombre = self.instance.usuario_toma_muestra.get_full_name()
                if not usuario_nombre:
                    usuario_nombre = self.instance.usuario_toma_muestra.username
                self.initial['usuario_toma_muestra_input'] = usuario_nombre
        
        # Formatear fechas para input type="date" al editar
        if self.instance.pk:
            if self.instance.fecha_solicitud:
                self.initial['fecha_solicitud'] = self.instance.fecha_solicitud.isoformat()
            if self.instance.fecha_toma_muestra:
                self.initial['fecha_toma_muestra'] = self.instance.fecha_toma_muestra.isoformat()
            if self.instance.fecha_ingreso_laboratorio:
                self.initial['fecha_ingreso_laboratorio'] = self.instance.fecha_ingreso_laboratorio.isoformat()
            if self.instance.fecha_resultado:
                self.initial['fecha_resultado'] = self.instance.fecha_resultado.isoformat()
            
            # Establecer valores para campos choices
            if self.instance.tipo_examen:
                self.initial['tipo_examen'] = self.instance.tipo_examen
            if self.instance.tipo_muestra:
                self.initial['tipo_muestra'] = self.instance.tipo_muestra
            if self.instance.sensibilidad:
                self.initial['sensibilidad'] = self.instance.sensibilidad
        
        # Mostrar/ocultar campo "otro_tipo_muestra"
        if self.instance and self.instance.tipo_muestra != 'OTRO':
            self.fields['otro_tipo_muestra'].widget = forms.HiddenInput()
        else:
            self.fields['otro_tipo_muestra'].widget = forms.TextInput(attrs={ 
                'class': 'form-control',
                'placeholder': 'Especificar tipo de muestra'
            })

    def clean(self):
        cleaned_data = super().clean()
        fecha_resultado = cleaned_data.get('fecha_resultado')
        fecha_toma_muestra = cleaned_data.get('fecha_toma_muestra')
        tipo_muestra = cleaned_data.get('tipo_muestra')
        otro_tipo_muestra = cleaned_data.get('otro_tipo_muestra')
        paciente_id = cleaned_data.get('paciente_id')
        laboratorio_nombre = cleaned_data.get('laboratorio_display')
        usuario_toma_muestra_input = cleaned_data.get('usuario_toma_muestra_input')

        # Validar que se haya seleccionado un paciente
        if not paciente_id:
            raise ValidationError({
                'rut_busqueda': 'Debe seleccionar un paciente válido usando el buscador de RUT.'
            })
        
        try:
            paciente = PacientesPaciente.objects.get(pk=paciente_id)
            cleaned_data['paciente'] = paciente
        except PacientesPaciente.DoesNotExist:
            raise ValidationError({
                'rut_busqueda': 'El paciente seleccionado no existe.'
            })

        # Validar acceso al paciente según rol
        if self.user and hasattr(self.user, 'usuariosusuario'):
            if not self.user.is_superuser and self.user.usuariosusuario.rol != 'admin':
                establecimiento_usuario = self.user.usuariosusuario.establecimiento
                if paciente.establecimiento_salud != establecimiento_usuario:
                    raise ValidationError({
                        'rut_busqueda': 'No tiene permisos para asignar exámenes a pacientes de otros establecimientos.'
                    })

        # Validar laboratorio
        if laboratorio_nombre:
            cleaned_data['laboratorio'] = laboratorio_nombre

        # Validar usuario que tomó la muestra
        if usuario_toma_muestra_input and self.user:
            # Por simplicidad, asignar el usuario actual
            cleaned_data['usuario_toma_muestra'] = self.user

        # Validar fechas
        if fecha_resultado and fecha_toma_muestra and fecha_resultado < fecha_toma_muestra:
            raise ValidationError({
                'fecha_resultado': 'La fecha de resultado no puede ser anterior a la fecha de toma de muestra.'
            })
        
        # Validar tipo de muestra
        if tipo_muestra == 'OTRO' and not otro_tipo_muestra:
            raise ValidationError({
                'otro_tipo_muestra': 'Debe especificar el tipo de muestra cuando selecciona "Otro".'
            })
        
        return cleaned_data

    def save(self, commit=True):
        # Asignar paciente desde el campo hidden
        paciente_id = self.cleaned_data.get('paciente_id')
        if paciente_id:
            try:
                paciente = PacientesPaciente.objects.get(pk=paciente_id)
                self.instance.paciente = paciente
            except PacientesPaciente.DoesNotExist:
                pass
        
        # Asignar laboratorio desde el campo display
        laboratorio_nombre = self.cleaned_data.get('laboratorio_display')
        if laboratorio_nombre:
            self.instance.laboratorio = laboratorio_nombre
        
        # Asignar usuario de registro si es nuevo
        if not self.instance.pk and self.user:
            self.instance.usuario_registro = self.user
            
        if commit:
            self.instance.save()
            
        return self.instance