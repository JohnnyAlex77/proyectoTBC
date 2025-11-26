from django.db import models
from django.contrib.auth.models import User
from apps.pacientes.models import PacientesPaciente as Paciente
from apps.contactos.models import ContactosContacto as Contacto
from datetime import date

class PrevencionQuimioprofilaxis(models.Model):
    TIPO_PACIENTE_CHOICES = [
        ('paciente', 'Paciente'),
        ('contacto', 'Contacto'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('suspendido', 'Suspendido'),
        ('abandonado', 'Abandonado'),
    ]
    
    MEDICAMENTOS_CHOICES = [
        ('isoniacida', 'Isoniacida (H)'),
        ('rifampicina', 'Rifampicina (R)'),
        ('combinado', 'Combinado HR'),
    ]

    tipo_paciente = models.CharField(max_length=10, choices=TIPO_PACIENTE_CHOICES)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    medicamento = models.CharField(max_length=20, choices=MEDICAMENTOS_CHOICES)
    dosis = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_termino_prevista = models.DateField()
    fecha_termino_real = models.DateField(null=True, blank=True)
    esquema = models.CharField(max_length=50)
    adherencia_porcentaje = models.IntegerField(default=0)
    efectos_adversos = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prevencion_quimioprofilaxis'
        verbose_name_plural = 'Quimioprofilaxis'

    def __str__(self):
        nombre = self.paciente.nombre if self.paciente else self.contacto.nombre
        return f"Quimioprofilaxis - {nombre}"

    def dias_tratamiento(self):
        if self.fecha_inicio:
            delta = date.today() - self.fecha_inicio
            return delta.days
        return 0

class PrevencionVacunacionBCG(models.Model):
    REACCION_CHOICES = [
        ('ninguna', 'Ninguna'),
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('severa', 'Severa'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha_vacunacion = models.DateField()
    lote = models.CharField(max_length=50)
    establecimiento = models.CharField(max_length=200)
    reaccion = models.CharField(max_length=10, choices=REACCION_CHOICES, default='ninguna')
    observaciones_reaccion = models.TextField(blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prevencion_vacunacion_bcg'
        verbose_name_plural = 'Vacunaciones BCG'

    def __str__(self):
        return f"BCG - {self.paciente.nombre} - {self.fecha_vacunacion}"

class PrevencionSeguimiento(models.Model):
    TIPO_SEGUIMIENTO_CHOICES = [
        ('quimioprofilaxis', 'Quimioprofilaxis'),
        ('vacunacion', 'Vacunación'),
    ]

    tipo_seguimiento = models.CharField(max_length=20, choices=TIPO_SEGUIMIENTO_CHOICES)
    quimioprofilaxis = models.ForeignKey(PrevencionQuimioprofilaxis, on_delete=models.CASCADE, null=True, blank=True)
    vacunacion = models.ForeignKey(PrevencionVacunacionBCG, on_delete=models.CASCADE, null=True, blank=True)
    fecha_seguimiento = models.DateField()
    resultado = models.TextField()
    observaciones = models.TextField(blank=True)
    proximo_control = models.DateField(null=True, blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)  # CORREGIDO: auto_now_add=True

    class Meta:
        db_table = 'prevencion_seguimiento'
        verbose_name_plural = 'Seguimientos Prevención'

    def __str__(self):
        return f"Seguimiento - {self.fecha_seguimiento}"