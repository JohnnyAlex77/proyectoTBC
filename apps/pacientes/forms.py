from django import forms
from django.core.exceptions import ValidationError
from .models import PacientesPaciente
import re

class PacienteForm(forms.ModelForm):
    # Campos adicionales para el formulario
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
                'placeholder': '12.345.678-9',
                'id': 'rut-input'
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
            # Mostrar RUT en formato con puntos para edición
            if self.instance.rut:
                self.initial['rut'] = self.formatear_rut_con_puntos(self.instance.rut)

    def clean_rut(self):
        """
        Valida y normaliza el formato del RUT a: 18444840-8 (sin puntos, con guión)
        Acepta cualquier formato de entrada y lo normaliza
        """
        rut = self.cleaned_data.get('rut', '').strip().upper()
        
        if not rut:
            raise ValidationError('El RUT es obligatorio')
        
        # Normalizar el RUT
        rut_normalizado = self.normalizar_rut(rut)
        
        # Validar formato del RUT normalizado
        if not self.validar_formato_rut(rut_normalizado):
            raise ValidationError('Formato de RUT inválido. Use formato: 12.345.678-9 o 12345678-9')
        
        return rut_normalizado

    def normalizar_rut(self, rut):
        """
        Normaliza cualquier formato de RUT al formato estándar: 18444840-8
        """
        # Eliminar puntos, espacios y convertir a mayúsculas
        rut = rut.replace('.', '').replace(' ', '').upper()
        
        # Separar número y dígito verificador
        if '-' in rut:
            partes = rut.split('-')
            if len(partes) == 2:
                numero = partes[0]
                dv = partes[1]
            else:
                # Si hay múltiples guiones, tomar el último como dígito verificador
                numero = ''.join(partes[:-1])
                dv = partes[-1]
        else:
            # Si no hay guión, asumir que el último carácter es el dígito verificador
            numero = rut[:-1]
            dv = rut[-1]
        
        # Validar que el número sea solo dígitos
        if not numero.isdigit():
            raise ValidationError('La parte numérica del RUT debe contener solo dígitos')
        
        # Validar dígito verificador (puede ser K o dígito)
        if not (dv.isdigit() or dv == 'K'):
            raise ValidationError('Dígito verificador inválido. Debe ser un número o K')
        
        # Retornar en formato normalizado: 18444840-8
        return f"{numero}-{dv}"

    def validar_formato_rut(self, rut):
        """
        Valida que el RUT tenga el formato correcto: 12345678-9
        """
        # Patrón: 1-8 dígitos, guión, dígito o K
        patron = r'^\d{1,8}-[\dK]$'
        return bool(re.match(patron, rut))

    def formatear_rut_con_puntos(self, rut):
        """
        Formatea el RUT para mostrar con puntos: 18.444.840-8
        Solo para visualización, no para almacenamiento
        """
        if not rut or '-' not in rut:
            return rut
        
        numero, dv = rut.split('-')
        
        # Formatear con puntos cada 3 dígitos desde el final
        numero_formateado = ''
        while len(numero) > 3:
            numero_formateado = '.' + numero[-3:] + numero_formateado
            numero = numero[:-3]
        numero_formateado = numero + numero_formateado
        
        return f"{numero_formateado}-{dv}"