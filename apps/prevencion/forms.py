from django import forms
from django.db.models import Q
from .models import PrevencionQuimioprofilaxis, PrevencionVacunacionBCG, PrevencionSeguimiento
from apps.pacientes.models import PacientesPaciente
from apps.contactos.models import ContactosContacto

class QuimioprofilaxisForm(forms.ModelForm):
    """
    Formulario para quimioprofilaxis con control de acceso y buscador por RUT
    """
    
    # Campo para búsqueda por RUT
    rut_busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese RUT para buscar paciente o contacto...',
            'id': 'rut-busqueda'
        }),
        label='Buscar por RUT'
    )
    
    # Campo para mostrar resultados de búsqueda
    resultado_busqueda = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'resultado-busqueda'}),
        label=''
    )

    class Meta:
        model = PrevencionQuimioprofilaxis
        fields = [
            'tipo_paciente', 'paciente', 'contacto', 'rut_busqueda', 'resultado_busqueda',
            'medicamento', 'dosis', 'fecha_inicio', 'fecha_termino_prevista', 
            'fecha_termino_real', 'esquema', 'estado', 'adherencia_porcentaje', 
            'efectos_adversos', 'observaciones'
        ]
        widgets = {
            'tipo_paciente': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_tipo_paciente',
                'onchange': 'toggleTipoPaciente()'
            }),
            'paciente': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_paciente'
            }),
            'contacto': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_contacto'
            }),
            'medicamento': forms.Select(attrs={'class': 'form-select'}),
            'dosis': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 300mg diarios'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'fecha_termino_prevista': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'fecha_termino_real': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'esquema': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 6H - 6 meses de Isoniacida'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'adherencia_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0', 
                'max': '100'
            }),
            'efectos_adversos': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Describa cualquier efecto adverso presentado...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Observaciones adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Hacer campos opcionales inicialmente
        self.fields['paciente'].required = False
        self.fields['contacto'].required = False
        
        # Filtrar pacientes y contactos según permisos del usuario
        if self.user:
            # Filtrar pacientes activos según establecimiento
            pacientes_qs = PacientesPaciente.objects.filter(estado='activo')
            if not self._usuario_tiene_acceso_completo():
                establecimiento = self._obtener_establecimiento_usuario()
                if establecimiento:
                    pacientes_qs = pacientes_qs.filter(establecimiento_salud=establecimiento)
            
            # Actualizar el queryset del campo paciente
            self.fields['paciente'].queryset = pacientes_qs
            
            # Filtrar contactos según establecimiento
            contactos_qs = ContactosContacto.objects.all()
            if not self._usuario_tiene_acceso_completo():
                establecimiento = self._obtener_establecimiento_usuario()
                if establecimiento:
                    contactos_qs = contactos_qs.filter(
                        paciente_indice__establecimiento_salud=establecimiento
                    )
            
            # Actualizar el queryset del campo contacto
            self.fields['contacto'].queryset = contactos_qs
        
        # Formatear fechas para que se muestren en los inputs
        if self.instance and self.instance.pk:
            if self.instance.fecha_inicio:
                self.initial['fecha_inicio'] = self.instance.fecha_inicio.strftime('%Y-%m-%d')
            if self.instance.fecha_termino_prevista:
                self.initial['fecha_termino_prevista'] = self.instance.fecha_termino_prevista.strftime('%Y-%m-%d')
            if self.instance.fecha_termino_real:
                self.initial['fecha_termino_real'] = self.instance.fecha_termino_real.strftime('%Y-%m-%d')

    def _usuario_tiene_acceso_completo(self):
        """Verifica si el usuario tiene acceso completo"""
        return (self.user.has_perm('prevencion.view_all_quimioprofilaxis') or 
                self.user.is_superuser or
                self._es_administrador())

    def _es_administrador(self):
        """Verifica si el usuario es administrador"""
        return (hasattr(self.user, 'usuariosusuario') and 
                getattr(self.user.usuariosusuario, 'es_administrador', False))

    def _obtener_establecimiento_usuario(self):
        """Obtiene el establecimiento del usuario de forma segura"""
        if hasattr(self.user, 'usuariosusuario'):
            return getattr(self.user.usuariosusuario, 'establecimiento', None)
        return None

    def clean(self):
        """Validación personalizada del formulario"""
        cleaned_data = super().clean()
        tipo_paciente = cleaned_data.get('tipo_paciente')
        paciente = cleaned_data.get('paciente')
        contacto = cleaned_data.get('contacto')
        
        # Validar que se seleccione paciente o contacto según el tipo
        if tipo_paciente == 'paciente' and not paciente:
            self.add_error('paciente', 'Debe seleccionar un paciente cuando el tipo es "Paciente"')
        elif tipo_paciente == 'contacto' and not contacto:
            self.add_error('contacto', 'Debe seleccionar un contacto cuando el tipo es "Contacto"')
        
        # Validar que no se seleccionen ambos
        if paciente and contacto:
            self.add_error('paciente', 'Solo puede seleccionar paciente o contacto, no ambos')
            self.add_error('contacto', 'Solo puede seleccionar paciente o contacto, no ambos')
        
        return cleaned_data


class VacunacionBCGForm(forms.ModelForm):
    """
    Formulario para vacunación BCG con control de acceso
    """
    
    class Meta:
        model = PrevencionVacunacionBCG
        fields = [
            'paciente', 'fecha_vacunacion', 'lote', 'establecimiento',
            'reaccion', 'observaciones_reaccion'
        ]
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'fecha_vacunacion': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'establecimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'reaccion': forms.Select(attrs={'class': 'form-select'}),
            'observaciones_reaccion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar pacientes según permisos del usuario
        if self.user:
            pacientes_qs = PacientesPaciente.objects.filter(estado='activo')
            if not self._usuario_tiene_acceso_completo():
                establecimiento = self._obtener_establecimiento_usuario()
                if establecimiento:
                    pacientes_qs = pacientes_qs.filter(establecimiento_salud=establecimiento)
            
            # Actualizar el queryset del campo paciente
            self.fields['paciente'].queryset = pacientes_qs
        
        if self.instance and self.instance.pk and self.instance.fecha_vacunacion:
            self.initial['fecha_vacunacion'] = self.instance.fecha_vacunacion.strftime('%Y-%m-%d')

    def _usuario_tiene_acceso_completo(self):
        """Verifica si el usuario tiene acceso completo"""
        return (self.user.has_perm('prevencion.view_all_vacunaciones') or 
                self.user.is_superuser or
                self._es_administrador())

    def _es_administrador(self):
        """Verifica si el usuario es administrador"""
        return (hasattr(self.user, 'usuariosusuario') and 
                getattr(self.user.usuariosusuario, 'es_administrador', False))

    def _obtener_establecimiento_usuario(self):
        """Obtiene el establecimiento del usuario de forma segura"""
        if hasattr(self.user, 'usuariosusuario'):
            return getattr(self.user.usuariosusuario, 'establecimiento', None)
        return None


class SeguimientoForm(forms.ModelForm):
    """
    Formulario para seguimientos con control de acceso
    """
    
    class Meta:
        model = PrevencionSeguimiento
        fields = [
            'tipo_seguimiento', 'quimioprofilaxis', 'vacunacion',
            'fecha_seguimiento', 'resultado', 'observaciones', 'proximo_control'
        ]
        widgets = {
            'tipo_seguimiento': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_tipo_seguimiento',
                'onchange': 'toggleTipoSeguimiento()'
            }),
            'quimioprofilaxis': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_quimioprofilaxis'
            }),
            'vacunacion': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_vacunacion'
            }),
            'fecha_seguimiento': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'proximo_control': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'resultado': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describa los resultados del seguimiento...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['quimioprofilaxis'].required = False
        self.fields['vacunacion'].required = False
        
        # Filtrar según permisos del usuario
        if self.user:
            # Filtrar quimioprofilaxis activas
            quimio_qs = PrevencionQuimioprofilaxis.objects.filter(estado='en_curso')
            if not self._usuario_tiene_acceso_completo():
                establecimiento = self._obtener_establecimiento_usuario()
                if establecimiento:
                    quimio_qs = quimio_qs.filter(
                        Q(paciente__establecimiento_salud=establecimiento) |
                        Q(contacto__paciente_indice__establecimiento_salud=establecimiento)
                    )
            
            # Actualizar el queryset del campo quimioprofilaxis
            self.fields['quimioprofilaxis'].queryset = quimio_qs
            
            # Filtrar vacunaciones
            vacuna_qs = PrevencionVacunacionBCG.objects.all()
            if not self._usuario_tiene_acceso_completo():
                establecimiento = self._obtener_establecimiento_usuario()
                if establecimiento:
                    vacuna_qs = vacuna_qs.filter(
                        paciente__establecimiento_salud=establecimiento
                    )
            
            # Actualizar el queryset del campo vacunacion
            self.fields['vacunacion'].queryset = vacuna_qs
        
        # Pre-seleccionar quimioprofilaxis si viene por URL
        if self.request:
            quimioprofilaxis_id = self.request.GET.get('quimioprofilaxis')
            if quimioprofilaxis_id:
                self.fields['quimioprofilaxis'].initial = quimioprofilaxis_id
                self.fields['tipo_seguimiento'].initial = 'quimioprofilaxis'

    def _usuario_tiene_acceso_completo(self):
        """Verifica si el usuario tiene acceso completo"""
        return (self.user.has_perm('prevencion.view_all_seguimientos') or 
                self.user.is_superuser or
                self._es_administrador())

    def _es_administrador(self):
        """Verifica si el usuario es administrador"""
        return (hasattr(self.user, 'usuariosusuario') and 
                getattr(self.user.usuariosusuario, 'es_administrador', False))

    def _obtener_establecimiento_usuario(self):
        """Obtiene el establecimiento del usuario de forma segura"""
        if hasattr(self.user, 'usuariosusuario'):
            return getattr(self.user.usuariosusuario, 'establecimiento', None)
        return None

    def clean(self):
        """Validación personalizada del formulario"""
        cleaned_data = super().clean()
        tipo_seguimiento = cleaned_data.get('tipo_seguimiento')
        quimioprofilaxis = cleaned_data.get('quimioprofilaxis')
        vacunacion = cleaned_data.get('vacunacion')
        
        # Validar que se seleccione según el tipo de seguimiento
        if tipo_seguimiento == 'quimioprofilaxis' and not quimioprofilaxis:
            self.add_error('quimioprofilaxis', 'Debe seleccionar una quimioprofilaxis para este tipo de seguimiento')
        elif tipo_seguimiento == 'vacunacion' and not vacunacion:
            self.add_error('vacunacion', 'Debe seleccionar una vacunación para este tipo de seguimiento')
        
        return cleaned_data