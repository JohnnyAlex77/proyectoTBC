# apps/pacientes/models.py
from django.db import models
from django.contrib.auth.models import User

class PacientesPaciente(models.Model):
    """
    Modelo principal para la gestión de pacientes con tuberculosis
    Incluye campos para antecedentes médicos y datos demográficos
    """
    
    # Opciones para sexo
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    # Opciones para tipo de tuberculosis
    TIPO_TBC_CHOICES = [
        ('pulmonar', 'TBC Pulmonar'),
        ('extrapulmonar', 'TBC Extrapulmonar'),
        ('mixta', 'TBC Mixta'),
    ]

    # Opciones para estado del paciente
    ESTADO_CHOICES = [
        ('activo', 'Activo en tratamiento'),
        ('suspendido', 'Tratamiento suspendido'),
        ('egresado', 'Egresado'),
        ('abandono', 'Abandono'),
        ('fallecido', 'Fallecido'),
    ]

    # Opciones para población prioritaria
    POBLACION_PRIORITARIA_CHOICES = [
        ('', 'No aplica'),
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

    # Campos principales del paciente
    id = models.BigAutoField(primary_key=True)
    rut = models.CharField(unique=True, max_length=12)  # Guardado como 18444840-8
    nombre = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    domicilio = models.TextField()
    comuna = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    establecimiento_salud = models.CharField(max_length=100)
    fecha_diagnostico = models.DateField(blank=True, null=True)
    tipo_tbc = models.CharField(max_length=50, choices=TIPO_TBC_CHOICES)
    baciloscopia_inicial = models.CharField(max_length=50, blank=True, null=True)
    cultivo_inicial = models.CharField(max_length=50, blank=True, null=True)
    poblacion_prioritaria = models.CharField(
        max_length=100,
        choices=POBLACION_PRIORITARIA_CHOICES,
        blank=True,
        null=True,
        default=''
    )
    
    # Antecedentes médicos
    enfermedades_preexistentes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Enfermedades preexistentes del paciente"
    )
    alergias = models.TextField(
        blank=True, 
        null=True, 
        help_text="Alergias conocidas del paciente"
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pacientes_paciente'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-fecha_registro']

    def __str__(self):
        """Representación en string del paciente"""
        return f"{self.nombre} ({self.rut})"

    def get_edad(self):
        """
        Calcula la edad del paciente en años
        Retorna: int - Edad del paciente
        """
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    def get_sexo_display(self):
        """Método manual para obtener el display del sexo"""
        sexo_dict = dict(self.SEXO_CHOICES)
        return sexo_dict.get(self.sexo, self.sexo)

    def get_tipo_tbc_display(self):
        """Método manual para obtener el display del tipo de TBC"""
        tipo_dict = dict(self.TIPO_TBC_CHOICES)
        return tipo_dict.get(self.tipo_tbc, self.tipo_tbc)

    def get_estado_display(self):
        """Método manual para obtener el display del estado"""
        estado_dict = dict(self.ESTADO_CHOICES)
        return estado_dict.get(self.estado, self.estado)

    def get_poblacion_prioritaria_display(self):
        """Método manual para obtener el display de población prioritaria"""
        poblacion_dict = dict(self.POBLACION_PRIORITARIA_CHOICES)
        # Verificar si el valor no es None ni vacío
        if self.poblacion_prioritaria:
            return poblacion_dict.get(self.poblacion_prioritaria, self.poblacion_prioritaria)
        return "No aplica"

    def get_enfermedades_list(self):
        """
        Convierte el texto de enfermedades en lista
        Retorna: list - Lista de enfermedades preexistentes
        """
        if self.enfermedades_preexistentes:
            return [enfermedad.strip() for enfermedad in self.enfermedades_preexistentes.split(',') if enfermedad.strip()]
        return []

    def get_alergias_list(self):
        """
        Convierte el texto de alergias en lista
        Retorna: list - Lista de alergias conocidas
        """
        if self.alergias:
            return [alergia.strip() for alergia in self.alergias.split(',') if alergia.strip()]
        return []

    def tiene_tratamiento_activo(self):
        """
        Verifica si el paciente tiene un tratamiento activo
        Retorna: bool - True si tiene tratamiento activo
        """
        from apps.tratamientos.models import Tratamiento
        return Tratamiento.objects.filter(
            paciente=self,
            resultado_final__in=[None, 'En Tratamiento']
        ).exists()
    
    def get_rut_formateado(self):
        """Devuelve el RUT formateado con puntos: 12.345.678-9"""
        if not self.rut or '-' not in self.rut:
            return self.rut
        
        numero, dv = self.rut.split('-')
        numero_formateado = ''
        
        # Formatear con puntos cada 3 dígitos desde el final
        while len(numero) > 3:
            numero_formateado = '.' + numero[-3:] + numero_formateado
            numero = numero[:-3]
        numero_formateado = numero + numero_formateado
        
        return f"{numero_formateado}-{dv}"