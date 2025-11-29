from django.db import models
from django.contrib.auth.models import User
from apps.pacientes.models import PacientesPaciente as Paciente

class Tratamiento(models.Model):
    """
    Modelo principal para gestionar tratamientos de pacientes con tuberculosis
    """
    
    # Opciones para esquemas terapéuticos
    ESQUEMA_OPCIONES = [
        ('HRZE', 'HRZE - Isoniazida, Rifampicina, Pirazinamida, Etambutol'),
        ('HRE', 'HRE - Isoniazida, Rifampicina, Etambutol'),
        ('HR', 'HR - Isoniazida, Rifampicina'),
        ('Personalizado', 'Esquema Personalizado'),
    ]

    # Relación con el paciente
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='tratamientos',
        verbose_name='Paciente'
    )
    
    # Esquema terapéutico
    esquema = models.CharField(
        max_length=50,
        choices=ESQUEMA_OPCIONES,
        verbose_name='Esquema Terapéutico'
    )
    
    # Fechas del tratamiento
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_termino_estimada = models.DateField(verbose_name='Fecha Término Estimada')
    fecha_termino_real = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Término Real'
    )
    
    # Información clínica
    peso_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Peso (kg)'
    )

    # Opciones para resultados finales
    RESULTADO_OPCIONES = [
        ('Curación', 'Curación'),
        ('Tratamiento Completo', 'Tratamiento Completo'),
        ('Fallecimiento', 'Fallecimiento'),
        ('Fracaso', 'Fracaso'),
        ('Abandono', 'Abandono'),
        ('Transferencia', 'Transferencia'),
        ('En Tratamiento', 'En Tratamiento'),
    ]
    
    resultado_final = models.CharField(
        max_length=50,
        choices=RESULTADO_OPCIONES,
        null=True,
        blank=True,
        verbose_name='Resultado Final'
    )

    # Observaciones adicionales
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='tratamientos_registrados',
        verbose_name='Usuario que registró'
    )

    class Meta:
        """Configuración del modelo"""
        db_table = 'tratamientos_tratamiento'
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        """Representación en string del tratamiento"""
        return f"Tratamiento {self.id} - {self.paciente.nombre} ({self.esquema})"

    @property
    def duracion_dias(self):
        """Calcula la duración del tratamiento en días"""
        if self.fecha_termino_real:
            return (self.fecha_termino_real - self.fecha_inicio).days
        return (self.fecha_termino_estimada - self.fecha_inicio).days

    @property
    def esta_activo(self):
        """Determina si el tratamiento está activo"""
        return self.resultado_final is None or self.resultado_final == 'En Tratamiento'

class EsquemaMedicamento(models.Model):
    """
    Modelo para gestionar los medicamentos dentro de un esquema de tratamiento
    """
    
    # Opciones para medicamentos
    MEDICAMENTO_OPCIONES = [
        ('Isoniazida (H)', 'Isoniazida (H)'),
        ('Rifampicina (R)', 'Rifampicina (R)'),
        ('Pirazinamida (Z)', 'Pirazinamida (Z)'),
        ('Etambutol (E)', 'Etambutol (E)'),
        ('Estreptomicina (S)', 'Estreptomicina (S)'),
        ('Levofloxacino', 'Levofloxacino'),
        ('Moxifloxacino', 'Moxifloxacino'),
        ('Amikacina', 'Amikacina'),
        ('Kanamicina', 'Kanamicina'),
        ('Capreomicina', 'Capreomicina'),
    ]

    # Opciones para frecuencia de administración
    FRECUENCIA_OPCIONES = [
        ('Diaria', 'Diaria'),
        ('3 veces por semana', '3 veces por semana'),
        ('2 veces por semana', '2 veces por semana'),
        ('Semanal', 'Semanal'),
    ]

    # Opciones para fases del tratamiento
    FASES_OPCIONES = [
        ('Fase Intensiva', 'Fase Intensiva'),
        ('Fase Continuación', 'Fase Continuación'),
        ('Fase Completa', 'Fase Completa'),
    ]

    # Relación con el tratamiento
    tratamiento = models.ForeignKey(
        Tratamiento,
        on_delete=models.CASCADE,
        related_name='esquemas_medicamento'
    )
    
    # Información del medicamento
    medicamento = models.CharField(max_length=100, choices=MEDICAMENTO_OPCIONES)
    dosis_mg = models.IntegerField(verbose_name='Dosis (mg)')
    frecuencia = models.CharField(max_length=50, choices=FRECUENCIA_OPCIONES)
    fase = models.CharField(max_length=50, choices=FASES_OPCIONES)
    duracion_semanas = models.IntegerField(verbose_name='Duración (semanas)')
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()

    class Meta:
        """Configuración del modelo"""
        db_table = 'tratamientos_esquemamedicamento'
        verbose_name = 'Esquema de Medicamento'
        verbose_name_plural = 'Esquemas de Medicamento'

    def __str__(self):
        """Representación en string del esquema de medicamento"""
        return f"{self.medicamento} - {self.dosis_mg}mg - {self.frecuencia}"

class DosisAdministrada(models.Model):
    """
    Modelo para registrar la administración de dosis de medicamentos
    """
    
    # Relación con el esquema de medicamento
    esquema_medicamento = models.ForeignKey(
        EsquemaMedicamento,
        on_delete=models.CASCADE,
        related_name='dosis_administradas'
    )
    
    # Información de la dosis
    fecha_dosis = models.DateField(verbose_name='Fecha de Dosis')
    administrada = models.BooleanField(default=False, verbose_name='¿Administrada?')
    hora_administracion = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Administración'
    )
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_administracion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='dosis_administradas',
        verbose_name='Usuario que administró'
    )

    class Meta:
        """Configuración del modelo"""
        db_table = 'tratamientos_dosisadministrada'
        verbose_name = 'Dosis Administrada'
        verbose_name_plural = 'Dosis Administradas'
        unique_together = ['esquema_medicamento', 'fecha_dosis']

    def __str__(self):
        """Representación en string de la dosis administrada"""
        estado = "✓" if self.administrada else "✗"
        return f"{estado} {self.fecha_dosis} {self.esquema_medicamento.medicamento}"