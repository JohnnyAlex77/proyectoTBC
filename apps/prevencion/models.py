from django.db import models
from django.contrib.auth.models import User
from apps.pacientes.models import PacientesPaciente as Paciente
from apps.contactos.models import ContactosContacto as Contacto
from datetime import date
from decimal import Decimal

class PrevencionQuimioprofilaxis(models.Model):
    """
    Modelo para gestión de quimioprofilaxis en prevención de TBC
    """
    
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

    # Campos principales
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
        """Representación en string de la quimioprofilaxis"""
        nombre = self.get_nombre_paciente_contacto()
        return f"Quimioprofilaxis - {nombre}"

    def get_nombre_paciente_contacto(self):
        """Obtiene el nombre del paciente o contacto"""
        if self.paciente:
            return self.paciente.nombre
        elif self.contacto:
            # Acceso seguro al atributo nombre_contacto
            return self.contacto.nombre_contacto if hasattr(self.contacto, 'nombre_contacto') else str(self.contacto)
        return "Sin nombre"

    def dias_tratamiento(self):
        """Calcula los días de tratamiento transcurridos"""
        if self.fecha_inicio:
            delta = date.today() - self.fecha_inicio
            return delta.days
        return 0

    def get_estado_display(self):
        """Método manual para obtener el display del estado"""
        return dict(self.ESTADO_CHOICES).get(self.estado, self.estado)

    def get_medicamento_display(self):
        """Método manual para obtener el display del medicamento"""
        return dict(self.MEDICAMENTOS_CHOICES).get(self.medicamento, self.medicamento)

    def get_tipo_paciente_display(self):
        """Método manual para obtener el display del tipo de paciente"""
        return dict(self.TIPO_PACIENTE_CHOICES).get(self.tipo_paciente, self.tipo_paciente)


class PrevencionVacunacionBCG(models.Model):
    """
    Modelo para registro de vacunaciones BCG
    """
    
    REACCION_CHOICES = [
        ('ninguna', 'Ninguna'),
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('severa', 'Severa'),
    ]

    # Campos principales
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

    def get_reaccion_display(self):
        """Método manual para obtener el display de la reacción"""
        return dict(self.REACCION_CHOICES).get(self.reaccion, self.reaccion)


class PrevencionSeguimiento(models.Model):
    """
    Modelo para seguimiento de actividades de prevención
    """
    
    TIPO_SEGUIMIENTO_CHOICES = [
        ('quimioprofilaxis', 'Quimioprofilaxis'),
        ('vacunacion', 'Vacunación'),
    ]

    # Campos principales
    tipo_seguimiento = models.CharField(max_length=20, choices=TIPO_SEGUIMIENTO_CHOICES)
    quimioprofilaxis = models.ForeignKey(
        PrevencionQuimioprofilaxis, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    vacunacion = models.ForeignKey(
        PrevencionVacunacionBCG, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    fecha_seguimiento = models.DateField()
    resultado = models.TextField()
    observaciones = models.TextField(blank=True)
    proximo_control = models.DateField(null=True, blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prevencion_seguimiento'
        verbose_name_plural = 'Seguimientos Prevención'

    def __str__(self):
        return f"Seguimiento - {self.fecha_seguimiento}"

    def get_tipo_seguimiento_display(self):
        """Método manual para obtener el display del tipo de seguimiento"""
        return dict(self.TIPO_SEGUIMIENTO_CHOICES).get(self.tipo_seguimiento, self.tipo_seguimiento)