# apps/examenes/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User  # Importar el modelo User de Django
from .models import ExamenesExamenbacteriologico, ExamenRadiologico, ExamenPPD
from apps.pacientes.models import PacientesPaciente

class ExamenBacteriologicoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=PacientesPaciente.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Paciente"
    )

    fecha_solicitud = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha de Solicitud",
    )
    
    fecha_toma_muestra = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha de Toma de Muestra"
    )
    
    fecha_ingreso_laboratorio = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha Ingreso Laboratorio"
    )
    
    fecha_resultado = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha Resultado"
    )

    # Campos con choices definidos explícitamente
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
    
    # Laboratorio como campo de texto por ahora
    laboratorio = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del laboratorio de referencia'
        }),
        label="Laboratorio de Referencia"
    )
    
    # CORRECCIÓN: Usar el modelo User de Django en lugar de UsuariosUsuario
    usuario_toma_muestra = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Usuario que tomó la muestra",
        empty_label="Seleccione un usuario"
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
        }
        
        labels = {
            'otro_tipo_muestra': 'Especificar otro tipo de muestra',
            'observaciones_muestra': 'Observaciones de la Muestra',
            'observaciones_resultado': 'Observaciones del Resultado',
            'numero_muestra_lab': 'Número de Muestra Laboratorio',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: Filtrar usuarios del modelo User de Django
        try:
            # Filtrar usuarios activos y ordenar por nombre
            usuarios_filtrados = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
            
            # Si necesitas filtrar por roles específicos, puedes hacerlo a través del modelo UsuariosUsuario
            # pero asignando el User relacionado
            try:
                from apps.usuarios.models import UsuariosUsuario
                # Obtener los Users que tienen los roles deseados en UsuariosUsuario
                usuarios_con_rol = UsuariosUsuario.objects.filter(
                    rol__in=['enfermera', 'tecnologo', 'paramedico']
                ).values_list('user_id', flat=True)
                
                # Filtrar los Users por esos IDs
                usuarios_filtrados = User.objects.filter(
                    id__in=usuarios_con_rol,
                    is_active=True
                ).order_by('first_name', 'last_name')
                
            except Exception as e:
                print(f"Error al filtrar por roles: {e}")
                # Si hay error, usar todos los usuarios activos
                usuarios_filtrados = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
            
            self.fields['usuario_toma_muestra'].queryset = usuarios_filtrados
            
        except Exception as e:
            # Si hay error, usar todos los usuarios activos
            print(f"Error al cargar usuarios: {e}")
            try:
                usuarios_filtrados = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
                self.fields['usuario_toma_muestra'].queryset = usuarios_filtrados
            except:
                # Si sigue fallando, cambiar a campo de texto
                self.fields['usuario_toma_muestra'] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Nombre del usuario que tomó la muestra'
                    }),
                    label="Usuario que tomó la muestra"
                )
        
        # Hacer campos opcionales
        self.fields['otro_tipo_muestra'].required = False
        self.fields['fecha_ingreso_laboratorio'].required = False
        self.fields['fecha_resultado'].required = False
        self.fields['resultado_cuantitativo'].required = False
        self.fields['resultado_cualitativo'].required = False
        self.fields['sensibilidad'].required = False
        self.fields['laboratorio'].required = False
        self.fields['numero_muestra_lab'].required = False
        self.fields['usuario_toma_muestra'].required = False
        
        # Establecer fecha_solicitud por defecto solo si es un nuevo registro
        if not self.instance.pk:  # Si es un nuevo registro
            self.fields['fecha_solicitud'].initial = timezone.now().date()
        
        # Formatear las fechas para el input type="date" al editar
        if self.instance.pk:  # Si estamos editando un registro existente
            # Convertir las fechas al formato YYYY-MM-DD requerido por input type="date"
            if self.instance.fecha_solicitud:
                self.initial['fecha_solicitud'] = self.instance.fecha_solicitud.isoformat()
            if self.instance.fecha_toma_muestra:
                self.initial['fecha_toma_muestra'] = self.instance.fecha_toma_muestra.isoformat()
            if self.instance.fecha_ingreso_laboratorio:
                self.initial['fecha_ingreso_laboratorio'] = self.instance.fecha_ingreso_laboratorio.isoformat()
            if self.instance.fecha_resultado:
                self.initial['fecha_resultado'] = self.instance.fecha_resultado.isoformat()
            
            # Asegurar que los campos con choices muestren el valor correcto
            if self.instance.tipo_examen:
                self.initial['tipo_examen'] = self.instance.tipo_examen
            if self.instance.tipo_muestra:
                self.initial['tipo_muestra'] = self.instance.tipo_muestra
            if self.instance.sensibilidad:
                self.initial['sensibilidad'] = self.instance.sensibilidad
        
        # Mostrar campo "otro_tipo_muestra" solo cuando se selecciona "OTRO"
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

        # Validar fechas
        if fecha_resultado and fecha_toma_muestra and fecha_resultado < fecha_toma_muestra:
            raise ValidationError("La fecha de resultado no puede ser anterior a la fecha de toma de muestra.")
        
        # Validar que si se selecciona "OTRO" en tipo de muestra, se complete el campo
        if tipo_muestra == 'OTRO' and not otro_tipo_muestra:
            raise ValidationError({
                'otro_tipo_muestra': 'Debe especificar el tipo de muestra cuando selecciona "Otro".'
            })
        return cleaned_data

class ExamenRadiologicoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=PacientesPaciente.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Paciente"
    )
    
    fecha_examen = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha del Examen"
    )

    # CORRECCIÓN: Definir explícitamente los campos con choices
    tipo_radiografia = forms.ChoiceField(
        choices=ExamenRadiologico.TIPO_RADIOGRAFIA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Radiografía"
    )
    
    hallazgos = forms.ChoiceField(
        choices=ExamenRadiologico.HALLAZGOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Hallazgos Principales"
    )

    class Meta:
        model = ExamenRadiologico
        fields = [
            'paciente', 'tipo_radiografia', 'fecha_examen', 'hallazgos',
            'descripcion_hallazgos', 'localizacion_lesiones',
            'establecimiento_realizacion', 'numero_informe', 'observaciones'
        ]
        
        widgets = {
            'descripcion_hallazgos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada de los hallazgos radiológicos'
            }),
            'localizacion_lesiones': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lóbulo superior derecho, campos medios'
            }),
            'establecimiento_realizacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del establecimiento'
            }),
            'numero_informe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de informe radiológico'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: Formatear la fecha para el input type="date" al editar
        if self.instance.pk and self.instance.fecha_examen:
            self.initial['fecha_examen'] = self.instance.fecha_examen.isoformat()
            
        # CORRECCIÓN: Asegurar que los campos con choices muestren el valor correcto
        if self.instance.pk:
            if self.instance.tipo_radiografia:
                self.initial['tipo_radiografia'] = self.instance.tipo_radiografia
            if self.instance.hallazgos:
                self.initial['hallazgos'] = self.instance.hallazgos

class ExamenPPDForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=PacientesPaciente.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Paciente"
    )
    
    fecha_aplicacion = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha de Aplicación"
    )
    
    fecha_lectura = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        ),
        label="Fecha de Lectura"
    )

    # CORRECCIÓN: Definir explícitamente los campos con choices
    resultado = forms.ChoiceField(
        choices=ExamenPPD.RESULTADO_PPD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Resultado"
    )
    
    lugar_aplicacion = forms.ChoiceField(
        choices=[
            ('BRAZO_DERECHO', 'Brazo Derecho'),
            ('BRAZO_IZQUIERDO', 'Brazo Izquierdo'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Lugar de Aplicación"
    )

    class Meta:
        model = ExamenPPD
        fields = [
            'paciente', 'fecha_aplicacion', 'fecha_lectura', 'milimetro_induration',
            'resultado', 'lugar_aplicacion', 'observaciones'
        ]
        
        widgets = {
            'milimetro_induration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50,
                'step': 1
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre la aplicación y lectura'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: Formatear las fechas para el input type="date" al editar
        if self.instance.pk:
            if self.instance.fecha_aplicacion:
                self.initial['fecha_aplicacion'] = self.instance.fecha_aplicacion.isoformat()
            if self.instance.fecha_lectura:
                self.initial['fecha_lectura'] = self.instance.fecha_lectura.isoformat()
            
        # CORRECCIÓN: Asegurar que los campos con choices muestren el valor correcto
        if self.instance.pk:
            if self.instance.resultado:
                self.initial['resultado'] = self.instance.resultado
            if self.instance.lugar_aplicacion:
                self.initial['lugar_aplicacion'] = self.instance.lugar_aplicacion

    def clean(self):
        cleaned_data = super().clean()
        fecha_aplicacion = cleaned_data.get('fecha_aplicacion')
        fecha_lectura = cleaned_data.get('fecha_lectura')

        if fecha_lectura and fecha_aplicacion:
            # Validar que la lectura sea entre 48-72 horas después
            dias_diferencia = (fecha_lectura - fecha_aplicacion).days
            if not (2 <= dias_diferencia <= 3):
                raise ValidationError({
                    'fecha_lectura': 'La lectura de PPD debe realizarse entre 48 y 72 horas después de la aplicación.'
                })
        return cleaned_data

class BuscarExamenesForm(forms.Form):
    TIPO_EXAMEN_CHOICES = [('','Todos los tipos')] + ExamenesExamenbacteriologico.TIPO_EXAMEN_CHOICES
    RESULTADO_CHOICES = [('','Todos los resultados')] + ExamenesExamenbacteriologico.RESULTADO_CHOICES
    ESTADO_CHOICES = [('','Todos los estados')] + ExamenesExamenbacteriologico.ESTADO_EXAMEN_CHOICES

    paciente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={ 
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o RUT del paciente'
        })
    )

    tipo_examen = forms.ChoiceField(
        required=False,
        choices=TIPO_EXAMEN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    resultado = forms.ChoiceField(
        required=False,
        choices=RESULTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estado_examen = forms.ChoiceField(
        required=False,
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )