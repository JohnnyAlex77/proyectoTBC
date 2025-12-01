# apps/contactos/forms.py
from django import forms
from .models import ContactosContacto
from apps.pacientes.models import PacientesPaciente

class ContactoForm(forms.ModelForm):
    # Campo de búsqueda para pacientes
    paciente_busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar paciente por nombre o RUT...',
            'id': 'paciente-busqueda'
        }),
        label='Buscar Paciente Índice'
    )
    
    class Meta:
        model = ContactosContacto
        fields = [
            'rut_contacto',
            'nombre_contacto',
            'paciente_indice',
            'parentesco',
            'tipo_contacto',
            'fecha_registro',
            'telefono',
            'estado_estudio'
        ]
        widgets = {
            'rut_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-9'
            }),
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del contacto'
            }),
            'paciente_indice': forms.Select(attrs={
                'class': 'form-control',
                'id': 'paciente-indice'
            }),
            'parentesco': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo_contacto': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_registro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'estado_estudio': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'rut_contacto': 'RUT Contacto',
            'nombre_contacto': 'Nombre Completo',
            'paciente_indice': 'Paciente Índice Seleccionado',
            'parentesco': 'Parentesco',
            'tipo_contacto': 'Tipo de Contacto',
            'fecha_registro': 'Fecha de Registro',
            'telefono': 'Teléfono',
            'estado_estudio': 'Estado del Estudio',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar pacientes según permisos del usuario
        if self.user:
            pacientes_qs = PacientesPaciente.objects.all()
            if not self.user.has_perm('contactos.view_all_contactos') and hasattr(self.user, 'perfilusuario'):
                establecimiento = self.user.perfilusuario.establecimiento
                pacientes_qs = pacientes_qs.filter(establecimiento_salud=establecimiento)
            
            # Actualizar el queryset del campo paciente_indice
            self.fields['paciente_indice'].queryset = pacientes_qs
        
        # Campos opcionales
        self.fields['telefono'].required = False
        
        # Si es una instancia existente (edición)
        if self.instance and self.instance.pk:
            # Hacer el RUT de solo lectura
            self.fields['rut_contacto'].widget.attrs['readonly'] = True
            self.fields['rut_contacto'].widget.attrs['class'] = 'form-control bg-light'
            
            # Pre-cargar el campo de búsqueda con el paciente actual
            if self.instance.paciente_indice:
                paciente_actual = self.instance.paciente_indice
                texto_paciente = f"{paciente_actual.nombre} - {paciente_actual.rut} - {paciente_actual.establecimiento_salud}"
                self.fields['paciente_busqueda'].initial = texto_paciente
        else:
            # Establecer fecha actual como valor por defecto para nuevos contactos
            from datetime import date
            self.fields['fecha_registro'].initial = date.today()

    def clean(self):
        """Validación adicional del formulario"""
        cleaned_data = super().clean()
        
        # Validar que se haya seleccionado un paciente
        paciente_indice = cleaned_data.get('paciente_indice')
        if not paciente_indice:
            raise forms.ValidationError({
                'paciente_indice': 'Debe seleccionar un paciente índice.'
            })
        
        return cleaned_data