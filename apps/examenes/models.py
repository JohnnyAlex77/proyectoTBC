# apps/examenes/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
        return f"{self.get_tipo_examen_display()} - {self.paciente} - {self.fecha_toma_muestra}"

    def clean(self):
        """Validaciones personalizadas"""
        errors = {}
        
        # Validar que la fecha de resultado no sea anterior a la fecha de toma de muestra
        if self.fecha_resultado and self.fecha_toma_muestra and self.fecha_resultado < self.fecha_toma_muestra:
            errors['fecha_resultado'] = 'La fecha de resultado no puede ser anterior a la fecha de toma de muestra.'
        
        # Validar que si hay resultado, debe tener fecha de resultado
        if self.resultado != 'PENDIENTE' and not self.fecha_resultado:
            errors['fecha_resultado'] = 'Si hay resultado disponible, debe especificar la fecha de resultado.'
        
        # Validar que si se especifica "otro" tipo de muestra, se complete el campo
        if self.tipo_muestra == 'OTRO' and not self.otro_tipo_muestra:
            errors['otro_tipo_muestra'] = 'Debe especificar el tipo de muestra cuando selecciona "Otro".'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Lógica adicional al guardar"""
        # Actualizar estado automáticamente según las fechas
        self.actualizar_estado()
        
        # Si hay resultado, actualizar fecha de actualización
        if self.resultado != 'PENDIENTE' and not self.fecha_resultado:
            self.fecha_resultado = timezone.now().date()
            
        super().save(*args, **kwargs)

    def actualizar_estado(self):
        """Actualizar estado del examen automáticamente"""
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
        """Calcula el tiempo de procesamiento en días"""
        if self.fecha_toma_muestra and self.fecha_resultado:
            return (self.fecha_resultado - self.fecha_toma_muestra).days
        return None

    @property
    def es_positivo(self):
        """Verifica si el resultado es positivo"""
        return self.resultado == 'POSITIVO'

    @property
    def tiene_resistencia(self):
        """Verifica si tiene algún tipo de resistencia"""
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
        """Verifica si es MDR (resistente al menos a Isoniazida y Rifampicina)"""
        return self.resistencia_isoniazida and self.resistencia_rifampicina

    @property
    def es_xdr(self):
        """Verifica si es XDR (MDR + resistencia a fluoroquinolonas y a un medicamento injectable)"""
        return (self.es_mdr and 
                self.resistencia_fluoroquinolonas and 
                self.resistencia_estreptomicina)

    def get_resistencias_detectadas(self):
        """Retorna lista de resistencias detectadas"""
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

    @property
    def estado_examen_display(self):
        """Propiedad para mostrar el estado del examen de forma legible"""
        if self.resultado == 'PENDIENTE':
            return 'Pendiente'
        elif self.resultado in ['POSITIVO', 'NEGATIVO']:
            return 'Completado'
        else:
            return 'Procesando'


# Modelo para Exámenes Radiológicos
class ExamenRadiologico(models.Model):
    TIPO_RADIOGRAFIA_CHOICES = [
        ('TORAX_AP', 'Radiografía de Tórax AP'),
        ('TORAX_PA', 'Radiografía de Tórax PA'),
        ('TORAX_LATERAL', 'Radiografía de Tórax Lateral'),
        ('OTRA', 'Otra Radiografía'),
    ]

    HALLAZGOS_CHOICES = [
        ('NORMAL', 'Normal'),
        ('COMPATIBLE_TBC', 'Compatible con TBC'),
        ('SUGERENTE_TBC', 'Sugerente de TBC'),
        ('INESPECIFICO', 'Hallazgos Inespecíficos'),
        ('OTRO', 'Otros Hallazgos'),
    ]

    paciente = models.ForeignKey(
        'pacientes.PacientesPaciente',
        on_delete=models.CASCADE,
        related_name='examenes_radiologicos'
    )

    tipo_radiografia = models.CharField(
        max_length=50,
        choices=TIPO_RADIOGRAFIA_CHOICES,
        verbose_name='Tipo de Radiografía'
    )
    fecha_examen = models.DateField(verbose_name='Fecha del Examen')
    hallazgos = models.CharField(
        max_length=50,
        choices=HALLAZGOS_CHOICES,
        verbose_name='Hallazgos Principales'
    )
    descripcion_hallazgos = models.TextField(
        verbose_name='Descripción Detallada de Hallazgos'
    )
    localizacion_lesiones = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Localización de Lesiones'
    )
    
    # Información del establecimiento
    establecimiento_realizacion = models.CharField(
        max_length=200,
        verbose_name='Establecimiento donde se realizó'
    )
    numero_informe = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Informe'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'examenes_radiologicos'
        verbose_name = 'Examen Radiológico'
        verbose_name_plural = 'Exámenes Radiológicos'
        ordering = ['-fecha_examen']

    def __str__(self):
        return f"Radiografía - {self.paciente} - {self.fecha_examen}"


# Modelo para Prueba de Tuberculina (PPD)
class ExamenPPD(models.Model):
    RESULTADO_PPD_CHOICES = [
        ('POSITIVO', 'Positivo'),
        ('NEGATIVO', 'Negativo'),
        ('INDETERMINADO', 'Indeterminado'),
        ('NO_LEIDO', 'No Leído'),
    ]

    paciente = models.ForeignKey(
        'pacientes.PacientesPaciente',
        on_delete=models.CASCADE,
        related_name='examenes_ppd'
    )

    fecha_aplicacion = models.DateField(verbose_name='Fecha de Aplicación')
    fecha_lectura = models.DateField(verbose_name='Fecha de Lectura')
    milimetro_induration = models.PositiveIntegerField(
        verbose_name='Milímetros de Induración',
        help_text='Milímetros de induración medida'
    )
    resultado = models.CharField(
        max_length=50,
        choices=RESULTADO_PPD_CHOICES,
        verbose_name='Resultado'
    )
    
    # Información de aplicación
    lugar_aplicacion = models.CharField(
        max_length=100,
        choices=[
            ('BRAZO_DERECHO', 'Brazo Derecho'),
            ('BRAZO_IZQUIERDO', 'Brazo Izquierdo'),
        ],
        default='BRAZO_DERECHO',
        verbose_name='Lugar de Aplicación'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    usuario_aplicacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ppd_aplicados',
        verbose_name='Usuario que aplicó la prueba'
    )
    usuario_lectura = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ppd_leidos',
        verbose_name='Usuario que leyó la prueba'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'examenes_ppd'
        verbose_name = 'Prueba de Tuberculina (PPD)'
        verbose_name_plural = 'Pruebas de Tuberculina (PPD)'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f"PPD - {self.paciente} - {self.fecha_aplicacion}"

    def clean(self):
        """Validaciones para PPD"""
        if self.fecha_lectura and self.fecha_lectura < self.fecha_aplicacion:
            raise ValidationError({
                'fecha_lectura': 'La fecha de lectura no puede ser anterior a la fecha de aplicación.'
            })
        
        # Validar que la lectura sea entre 48-72 horas después
        if self.fecha_lectura and self.fecha_aplicacion:
            dias_diferencia = (self.fecha_lectura - self.fecha_aplicacion).days
            if not (2 <= dias_diferencia <= 3):
                raise ValidationError({
                    'fecha_lectura': 'La lectura de PPD debe realizarse entre 48 y 72 horas después de la aplicación.'
                })

    @property
    def es_positivo_por_milimetros(self):
        """Determina si es positivo según los milímetros y factores de riesgo"""
        if self.milimetro_induration >= 10:
            return True
        elif self.milimetro_induration >= 5:
            # Considerar factores de riesgo del paciente
            # Se asume que el modelo Paciente tiene este método
            if hasattr(self.paciente, 'tiene_factores_riesgo_tbc'):
                return self.paciente.tiene_factores_riesgo_tbc()
            return False  # Por defecto si no existe el método
        return False