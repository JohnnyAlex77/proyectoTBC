from django.db import models
from django.contrib.auth.models import User
from apps.pacientes.models import PacientesPaciente
from apps.tratamientos.models import Tratamiento
from apps.contactos.models import ContactosContacto
from apps.prevencion.models import PrevencionQuimioprofilaxis
from datetime import datetime

class Establecimiento(models.Model):
    """Modelo de establecimiento para el módulo indicadores"""
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=100, default="Centro de Salud")
    region = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Establecimiento"
        verbose_name_plural = "Establecimientos"

    def __str__(self):
        return self.nombre

class IndicadoresCohorte(models.Model):
    """Indicadores de cohorte trimestrales PROCET"""
    ESTADOS_COHORTE = [
        ('Q1', 'Primer Trimestre'),
        ('Q2', 'Segundo Trimestre'),
        ('Q3', 'Tercer Trimestre'),
        ('Q4', 'Cuarto Trimestre'),
    ]

    año = models.IntegerField()
    trimestre = models.CharField(max_length=2, choices=ESTADOS_COHORTE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)

    # Casos
    casos_nuevos = models.IntegerField(default=0)
    casos_retratamiento = models.IntegerField(default=0)

    # Resultados tratamiento
    curados = models.IntegerField(default=0)
    abandonos = models.IntegerField(default=0)
    fallecidos = models.IntegerField(default=0)
    fracasos = models.IntegerField(default=0)
    trasladados = models.IntegerField(default=0)

    # Cálculos automáticos
    @property
    def total_casos(self):
        return self.casos_nuevos + self.casos_retratamiento

    @property
    def exito_tratamiento_porcentaje(self):
        if self.total_casos > 0:
            return round((self.curados / self.total_casos) * 100, 2)
        return 0

    @property
    def tasa_abandono(self):
        if self.total_casos > 0:
            return round((self.abandonos / self.total_casos) * 100, 2)
        return 0

    @property
    def tasa_fallecimiento(self):
        if self.total_casos > 0:
            return round((self.fallecidos / self.total_casos) * 100, 2)
        return 0

    class Meta:
        unique_together = ['año', 'trimestre', 'establecimiento']
        verbose_name = "Indicador de Cohorte"
        verbose_name_plural = "Indicadores de Cohorte"

    def __str__(self):
        return f"{self.año}-{self.trimestre} - {self.establecimiento}"

class IndicadoresOperacionales(models.Model):
    """Indicadores operacionales mensuales"""
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    periodo = models.DateField()  # Primer día del mes

    # Pesquisa
    sintomaticos_respiratorios = models.IntegerField(default=0)
    baciloscopias_realizadas = models.IntegerField(default=0)
    casos_tb_encontrados = models.IntegerField(default=0)

    # Contactos
    contactos_identificados = models.IntegerField(default=0)
    contactos_estudiados = models.IntegerField(default=0)

    # TAES
    pacientes_taes = models.IntegerField(default=0)
    pacientes_adherentes = models.IntegerField(default=0)

    # Tiempos
    tiempo_promedio_diagnostico = models.IntegerField(default=0)  # en horas

    @property
    def indice_pesquisa(self):
        if self.sintomaticos_respiratorios > 0:
            return round((self.baciloscopias_realizadas / self.sintomaticos_respiratorios) * 100, 2)
        return 0

    @property
    def cobertura_estudio_contactos(self):
        if self.contactos_identificados > 0:
            return round((self.contactos_estudiados / self.contactos_identificados) * 100, 2)
        return 0

    @property
    def adherencia_taes(self):
        if self.pacientes_taes > 0:
            return round((self.pacientes_adherentes / self.pacientes_taes) * 100, 2)
        return 0

    class Meta:
        unique_together = ['establecimiento', 'periodo']
        verbose_name = "Indicador Operacional"
        verbose_name_plural = "Indicadores Operacionales"

    def __str__(self):
        return f"Operacionales {self.periodo} - {self.establecimiento}"

class IndicadoresPrevencion(models.Model):
    """Indicadores de actividades preventivas"""
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    periodo = models.DateField()

    # Quimioprofilaxis
    contactos_elegibles_qp = models.IntegerField(default=0)
    contactos_iniciados_qp = models.IntegerField(default=0)
    contactos_completados_qp = models.IntegerField(default=0)

    # Vacunación BCG
    recien_nacidos = models.IntegerField(default=0)
    recien_nacidos_vacunados = models.IntegerField(default=0)

    # Tiempos
    tiempo_promedio_inicio_qp = models.IntegerField(default=0)  # en días

    @property
    def cobertura_quimioprofilaxis(self):
        if self.contactos_elegibles_qp > 0:
            return round((self.contactos_iniciados_qp / self.contactos_elegibles_qp) * 100, 2)
        return 0

    @property
    def adherencia_quimioprofilaxis(self):
        if self.contactos_iniciados_qp > 0:
            return round((self.contactos_completados_qp / self.contactos_iniciados_qp) * 100, 2)
        return 0

    @property
    def cobertura_vacunacion_bcg(self):
        if self.recien_nacidos > 0:
            return round((self.recien_nacidos_vacunados / self.recien_nacidos) * 100, 2)
        return 0

    class Meta:
        verbose_name = "Indicador de Prevención"
        verbose_name_plural = "Indicadores de Prevención"

    def __str__(self):
        return f"Prevención {self.periodo} - {self.establecimiento}"

class Alerta(models.Model):
    """Sistema de alertas y notificaciones"""

    TIPOS_ALERTA = [
        ('VENCIMIENTO', 'Vencimiento'),
        ('RESULTADO', 'Resultado'),
        ('SEGUIMIENTO', 'Seguimiento'),
        ('EPIDEMIOLOGICA', 'Alerta Epidemiológica'),
        ('CALIDAD', 'Calidad de Datos'),
    ]

    NIVELES_ALERTA = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS_ALERTA)
    nivel = models.CharField(max_length=10, choices=NIVELES_ALERTA)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    usuario_asignado = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    resuelta = models.BooleanField(default=False)
    datos_relacionados = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"

    def __str__(self):
        return f"{self.tipo} - {self.titulo}"

    @property
    def esta_vencida(self):
        from django.utils import timezone
        return not self.resuelta and timezone.now() > self.fecha_vencimiento

class ReportePersonalizado(models.Model):
    """Configuración de reportes personalizados"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    usuario_creador = models.ForeignKey(User, on_delete=models.CASCADE)

    # Configuración del reporte
    parametros = models.JSONField(default=dict, blank=True)
    columnas_visibles = models.JSONField(default=list, blank=True)
    filtros = models.JSONField(default=dict, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    compartido = models.BooleanField(default=False)
    usuarios_compartidos = models.ManyToManyField(
        User,
        related_name='reportes_compartidos',
        blank=True
    )

    class Meta:
        verbose_name = "Reporte Personalizado"
        verbose_name_plural = "Reportes Personalizados"

    def __str__(self):
        return self.nombre