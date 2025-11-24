from django.db import models
from django.contrib.auth.models import User

class PacientesPaciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    TIPO_TBC_CHOICES = [
        ('pulmonar', 'TBC Pulmonar'),
        ('extrapulmonar', 'TBC Extrapulmonar'),
        ('mixta', 'TBC Mixta'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo en tratamiento'),
        ('suspendido', 'Tratamiento suspendido'),
        ('egresado', 'Egresado'),
        ('abandono', 'Abandono'),
        ('fallecido', 'Fallecido'),
    ]

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

    id = models.BigAutoField(primary_key=True)
    rut = models.CharField(unique=True, max_length=12) 
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
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pacientes_paciente'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        return f"{self.nombre} ({self.rut})"  # CORREGIDO: self.put -> self.rut

    def get_edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )