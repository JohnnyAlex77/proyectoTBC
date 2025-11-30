# apps/examenes/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class ExamenesExamenbacteriologico(models.Model):
    TIPO_EXAMEN_CHOICES = [
        ('BACILOSCOPIA', 'Baciloscopia'),
        ('CULTIVO', 'Cultivo'),
        ('GENEXPERT', 'GeneXpert'),
        ('XPERTO', 'Xpert MTB/RIF'),
        ('LAM', 'LAM (Urinario)'),
        ('PPD', 'PPD (Tuberculina)'),
        ('RADIOGRAFIA', 'Radiografía de Tórax'),
        ('TAMIZAJE', 'Tamizaje Molecular'),
    ]

    TIPO_MUESTRA_CHOICES = [
        ('ESPUTO', 'Esputo'),
        ('ESPUTO_INDUCIDO', 'Esputo Inducido'),
        ('LAVADO_GASTRICO', 'Lavado Gástrico'),
        ('ASPIRADO', 'Aspirado Bronquial'),
        ('BIOPSIA', 'Biopsia'),
        ('SANGRE', 'Sangre'),
        ('ORINA', 'Orina'),
        ('LIQUIDO_CEFALORRAQUIDEO', 'Líquido Cefalorraquídeo'),
        ('LIQUIDO_PLEURAL', 'Líquido Pleural'),
        ('OTRO', 'Otro'),
    ]

    RESULTADO_CHOICES = [
        ('POSITIVO', 'Positivo'),
        ('NEGATIVO', 'Negativo'),
        ('INDETERMINADO', 'Indeterminado'),
        ('CONTAMINADO', 'Contaminado'),
        ('PENDIENTE', 'Pendiente'),
        ('NO_APLICA', 'No Aplica'),
    ]

    SENSIBILIDAD_CHOICES = [
        ('SENSIBLE', 'Sensible'),
        ('RESISTENTE', 'Resistente'),
        ('MONO_RESISTENTE', 'Mono-Resistente'),
        ('POLI_RESISTENTE', 'Poli-Resistente'),
        ('ULTRA_RESISTENTE', 'Ultra-Resistente'),
        ('MDR', 'MDR (Multidrogorresistente)'),
        ('XDR', 'XDR (Extensamente resistente)'),
        ('PENDIENTE', 'Pendiente'),
        ('NO_APLICA', 'No Aplica'),
    ]

    ESTADO_EXAMEN_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('MUESTRA_TOMADA', 'Muestra Tomada'),
        ('ENVIADO_LABORATORIO', 'Enviado a Laboratorio'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    # Información del Paciente
    paciente = models.ForeignKey(
        'pacientes.PacientesPaciente',
        on_delete=models.CASCADE,
        related_name='examenes_bacteriologicos'
    )

    # Información del Examen
    tipo_examen = models.CharField(
        max_length=100, 
        choices=TIPO_EXAMEN_CHOICES,
        verbose_name='Tipo de Examen'
    )
    tipo_muestra = models.CharField(
        max_length=100, 
        choices=TIPO_MUESTRA_CHOICES,
        verbose_name='Tipo de Muestra'
    )
    otro_tipo_muestra = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Especificar otro tipo de muestra'
    )

    # Fechas del Proceso
    fecha_solicitud = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Solicitud'
    )
    fecha_toma_muestra = models.DateField(
        verbose_name='Fecha de Toma de Muestra'
    )
    fecha_ingreso_laboratorio = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Fecha Ingreso Laboratorio'
    )
    fecha_resultado = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Fecha de Resultado'
    )

    # Resultados
    resultado = models.CharField(
        max_length=100, 
        choices=RESULTADO_CHOICES, 
        default='PENDIENTE',
        verbose_name='Resultado'
    )
    resultado_cuantitativo = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Resultado Cuantitativo'
    )
    resultado_cualitativo = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Resultado Cualitativo'
    )
    
    # Sensibilidad y Resistencia
    sensibilidad = models.CharField(
        max_length=100, 
        choices=SENSIBILIDAD_CHOICES, 
        blank=True, 
        null=True,
        verbose_name='Sensibilidad'
    )
    
    # Detalles de Resistencia
    resistencia_isoniazida = models.BooleanField(default=False, verbose_name='Resistente a Isoniazida')
    resistencia_rifampicina = models.BooleanField(default=False, verbose_name='Resistente a Rifampicina')
    resistencia_pirazinamida = models.BooleanField(default=False, verbose_name='Resistente a Pirazinamida')
    resistencia_etambutol = models.BooleanField(default=False, verbose_name='Resistente a Etambutol')
    resistencia_estreptomicina = models.BooleanField(default=False, verbose_name='Resistente a Estreptomicina')
    resistencia_fluoroquinolonas = models.BooleanField(default=False, verbose_name='Resistente a Fluoroquinolonas')
    
    # Información Adicional
    observaciones_muestra = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Observaciones de la Muestra'
    )
    observaciones_resultado = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Observaciones del Resultado'
    )
    
    # Estado y Seguimiento
    estado_examen = models.CharField(
        max_length=50, 
        choices=ESTADO_EXAMEN_CHOICES, 
        default='SOLICITADO',
        verbose_name='Estado del Examen'
    )
    prioridad = models.CharField(
        max_length=20,
        choices=[
            ('NORMAL', 'Normal'),
            ('URGENTE', 'Urgente'),
            ('EMERGENCIA', 'Emergencia'),
        ],
        default='NORMAL',
        verbose_name='Prioridad'
    )
    
    # Información de Laboratorio
    laboratorio = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Laboratorio de Referencia'
    )
    numero_muestra_lab = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Muestra Laboratorio'
    )
    
    # Metadatos
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='examenes_registrados'
    )
    usuario_toma_muestra = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='examenes_toma_muestra',
        verbose_name='Usuario que tomó la muestra'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'examenes_examenbacteriologico'
        verbose_name = 'Examen Bacteriológico'
        verbose_name_plural = 'Exámenes Bacteriológicos'
        ordering = ['-fecha_toma_muestra', '-fecha_registro']
        indexes = [
            models.Index(fields=['paciente', 'fecha_toma_muestra']),
            models.Index(fields=['tipo_examen', 'resultado']),
            models.Index(fields=['estado_examen']),
        ]

    def __str__(self):
        # Método manual para obtener display de tipo_examen
        tipo_display = self._get_choice_display(self.TIPO_EXAMEN_CHOICES, self.tipo_examen)
        return f"{tipo_display} - {self.paciente} - {self.fecha_toma_muestra}"

    def _get_choice_display(self, choices, value):
        """Método auxiliar para obtener display de campos choices"""
        if value is None:
            return ""
        choices_dict = dict(choices)
        return choices_dict.get(value, value)

    # Métodos manuales para obtener display de campos choices
    def get_tipo_examen_display(self):
        return self._get_choice_display(self.TIPO_EXAMEN_CHOICES, self.tipo_examen)

    def get_tipo_muestra_display(self):
        return self._get_choice_display(self.TIPO_MUESTRA_CHOICES, self.tipo_muestra)

    def get_resultado_display(self):
        return self._get_choice_display(self.RESULTADO_CHOICES, self.resultado)

    def get_sensibilidad_display(self):
        return self._get_choice_display(self.SENSIBILIDAD_CHOICES, self.sensibilidad)

    def get_estado_examen_display(self):
        return self._get_choice_display(self.ESTADO_EXAMEN_CHOICES, self.estado_examen)

    def clean(self):
        errors = {}
        
        if self.fecha_resultado and self.fecha_toma_muestra and self.fecha_resultado < self.fecha_toma_muestra:
            errors['fecha_resultado'] = 'La fecha de resultado no puede ser anterior a la fecha de toma de muestra.'
        
        if self.resultado != 'PENDIENTE' and not self.fecha_resultado:
            errors['fecha_resultado'] = 'Si hay resultado disponible, debe especificar la fecha de resultado.'
        
        if self.tipo_muestra == 'OTRO' and not self.otro_tipo_muestra:
            errors['otro_tipo_muestra'] = 'Debe especificar el tipo de muestra cuando selecciona "Otro".'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.actualizar_estado()
        
        if self.resultado != 'PENDIENTE' and not self.fecha_resultado:
            self.fecha_resultado = timezone.now().date()
            
        super().save(*args, **kwargs)

    def actualizar_estado(self):
        hoy = timezone.now().date()
        
        if self.resultado != 'PENDIENTE':
            self.estado_examen = 'COMPLETADO'
        elif self.fecha_ingreso_laboratorio:
            self.estado_examen = 'EN_PROCESO'
        elif self.fecha_toma_muestra:
            self.estado_examen = 'ENVIADO_LABORATORIO'
        else:
            self.estado_examen = 'SOLICITADO'

    @property
    def tiempo_procesamiento(self):
        if self.fecha_toma_muestra and self.fecha_resultado:
            return (self.fecha_resultado - self.fecha_toma_muestra).days
        return None

    @property
    def es_positivo(self):
        return self.resultado == 'POSITIVO'

    @property
    def tiene_resistencia(self):
        return any([
            self.resistencia_isoniazida,
            self.resistencia_rifampicina,
            self.resistencia_pirazinamida,
            self.resistencia_etambutol,
            self.resistencia_estreptomicina,
            self.resistencia_fluoroquinolonas
        ])

    @property
    def es_mdr(self):
        return self.resistencia_isoniazida and self.resistencia_rifampicina

    @property
    def es_xdr(self):
        return (self.es_mdr and 
                self.resistencia_fluoroquinolonas and 
                self.resistencia_estreptomicina)

    def get_resistencias_detectadas(self):
        resistencias = []
        if self.resistencia_isoniazida:
            resistencias.append('Isoniazida (H)')
        if self.resistencia_rifampicina:
            resistencias.append('Rifampicina (R)')
        if self.resistencia_pirazinamida:
            resistencias.append('Pirazinamida (Z)')
        if self.resistencia_etambutol:
            resistencias.append('Etambutol (E)')
        if self.resistencia_estreptomicina:
            resistencias.append('Estreptomicina (S)')
        if self.resistencia_fluoroquinolonas:
            resistencias.append('Fluoroquinolonas')
        return resistencias