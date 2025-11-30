from django.db import models
from django.contrib.auth.models import User
from apps.pacientes.models import PacientesPaciente as Paciente
from apps.examenes.models import ExamenesExamenbacteriologico as Examen
from decimal import Decimal

class LaboratorioRedLaboratorios(models.Model):
    TIPO_LABORATORIO_CHOICES = [
        ('I', 'Tipo I - Básico'),
        ('II', 'Tipo II - Intermedio'),
        ('III', 'Tipo III - Avanzado'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=3, choices=TIPO_LABORATORIO_CHOICES)
    direccion = models.CharField(max_length=300)
    comuna = models.CharField(max_length=100)
    responsable = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'laboratorio_red_laboratorios'
        verbose_name_plural = 'Red de Laboratorios'

    def get_tipo_display(self):
        """Método manual para obtener el display del tipo de laboratorio"""
        return dict(self.TIPO_LABORATORIO_CHOICES).get(self.tipo, self.tipo)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class LaboratorioControlCalidad(models.Model):
    TIPO_CONTROL_CHOICES = [
        ('peec', 'PEEC - Programa Externo'),
        ('interno', 'Control Interno'),
        ('interlaboratorio', 'Interlaboratorio'),
    ]
    
    RESULTADO_CHOICES = [
        ('satisfactorio', 'Satisfactorio'),
        ('insatisfactorio', 'Insatisfactorio'),
        ('pendiente', 'Pendiente'),
    ]

    laboratorio = models.ForeignKey(LaboratorioRedLaboratorios, on_delete=models.CASCADE)
    fecha_control = models.DateField()
    tipo_control = models.CharField(max_length=20, choices=TIPO_CONTROL_CHOICES)
    resultado = models.CharField(max_length=15, choices=RESULTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True)
    usuario_responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'laboratorio_control_calidad'
        verbose_name_plural = 'Controles de Calidad'

    def get_tipo_control_display(self):
        """Método manual para obtener el display del tipo de control"""
        return dict(self.TIPO_CONTROL_CHOICES).get(self.tipo_control, self.tipo_control)

    def get_resultado_display(self):
        """Método manual para obtener el display del resultado"""
        return dict(self.RESULTADO_CHOICES).get(self.resultado, self.resultado)

    def __str__(self):
        return f"Control {self.get_tipo_control_display()} - {self.laboratorio.nombre}"

class LaboratorioTarjetero(models.Model):
    TIPO_MUESTRA_CHOICES = [
        ('esputo', 'Esputo'),
        ('aspirado', 'Aspirado Gastrico'),
        ('lavado', 'Lavado Bronquial'),
        ('otros', 'Otros'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    fecha_deteccion = models.DateField()
    tipo_muestra = models.CharField(max_length=20, choices=TIPO_MUESTRA_CHOICES)
    resultado = models.CharField(max_length=100)
    laboratorio_referencia = models.ForeignKey(LaboratorioRedLaboratorios, on_delete=models.PROTECT)
    fecha_notificacion = models.DateField()
    usuario_notificador = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'laboratorio_tarjetero'
        verbose_name_plural = 'Tarjetero de Positivos'

    def get_tipo_muestra_display(self):
        """Método manual para obtener el display del tipo de muestra"""
        return dict(self.TIPO_MUESTRA_CHOICES).get(self.tipo_muestra, self.tipo_muestra)

    def __str__(self):
        return f"Tarjetero - {self.paciente.nombre} - {self.fecha_deteccion}"

class LaboratorioIndicadores(models.Model):
    laboratorio = models.ForeignKey(LaboratorioRedLaboratorios, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=7)
    muestras_recibidas = models.IntegerField(default=0)
    muestras_procesadas = models.IntegerField(default=0)
    positivos = models.IntegerField(default=0)
    contaminacion_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tiempo_respuesta_promedio = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'laboratorio_indicadores'
        verbose_name_plural = 'Indicadores Laboratorio'
        unique_together = ['laboratorio', 'periodo']

    def __str__(self):
        return f"Indicadores {self.laboratorio.nombre} - {self.periodo}"