"""
Serializadores para el dashboard API
Transforman estadísticas en JSON estructurado
"""
from rest_framework import serializers
from datetime import date, timedelta

class DashboardEstadisticasSerializer(serializers.Serializer):
    """
    Serializador para estadísticas generales del dashboard
    """
    # Pacientes
    total_pacientes = serializers.IntegerField()
    pacientes_activos = serializers.IntegerField()
    pacientes_nuevos_ultimo_mes = serializers.IntegerField()
    
    # Tratamientos
    total_tratamientos = serializers.IntegerField()
    tratamientos_activos = serializers.IntegerField()
    tratamientos_completados = serializers.IntegerField()
    tasa_exito_tratamientos = serializers.FloatField()
    
    # Exámenes
    total_examenes = serializers.IntegerField()
    examenes_positivos = serializers.IntegerField()
    examenes_pendientes = serializers.IntegerField()
    
    # Contactos
    total_contactos = serializers.IntegerField()
    contactos_estudiados = serializers.IntegerField()
    
    # Distribución por sexo
    pacientes_masculino = serializers.IntegerField()
    pacientes_femenino = serializers.IntegerField()
    pacientes_otro_sexo = serializers.IntegerField()
    
    # Distribución por tipo TBC
    tbc_pulmonar = serializers.IntegerField()
    tbc_extrapulmonar = serializers.IntegerField()
    tbc_miliar = serializers.IntegerField()
    
    # Distribución por estado
    pacientes_en_tratamiento = serializers.IntegerField()
    pacientes_curados = serializers.IntegerField()
    pacientes_fallecidos = serializers.IntegerField()
    pacientes_abandono = serializers.IntegerField()
    
    # Métricas adicionales
    edad_promedio = serializers.FloatField(allow_null=True)
    tasa_incidencia = serializers.FloatField(allow_null=True)
    alertas_activas = serializers.IntegerField()
    
    # Timestamps
    fecha_actualizacion = serializers.DateTimeField()
    periodo_desde = serializers.DateField()
    periodo_hasta = serializers.DateField()
    
    class Meta:
        fields = '__all__'


class TendenciaSerializer(serializers.Serializer):
    """
    Serializador para datos de tendencias temporales
    """
    periodo = serializers.DateField()
    casos_nuevos = serializers.IntegerField()
    tratamientos_iniciados = serializers.IntegerField()
    examenes_realizados = serializers.IntegerField()
    tasa_positividad = serializers.FloatField()
    
    class Meta:
        fields = '__all__'


class AlertaSerializer(serializers.Serializer):
    """
    Serializador para alertas del sistema
    """
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    nivel = serializers.CharField()
    mensaje = serializers.CharField()
    fecha = serializers.DateField()
    url = serializers.CharField()
    paciente_id = serializers.IntegerField(allow_null=True)
    paciente_nombre = serializers.CharField(allow_null=True)
    
    class Meta:
        fields = '__all__'


class DistribucionComunalSerializer(serializers.Serializer):
    """
    Serializador para distribución de casos por comuna
    """
    comuna = serializers.CharField()
    total_casos = serializers.IntegerField()
    porcentaje = serializers.FloatField()
    incidencia = serializers.FloatField()
    poblacion = serializers.IntegerField()
    
    class Meta:
        fields = '__all__'


class ResumenEjecutivoSerializer(serializers.Serializer):
    """
    Serializador para resumen ejecutivo del dashboard
    """
    # Métricas clave
    metricas_principales = serializers.DictField()
    
    # Tendencias
    tendencia_ultimo_mes = serializers.CharField()
    tendencia_ultimo_trimestre = serializers.CharField()
    
    # Alertas
    alertas_criticas = serializers.IntegerField()
    alertas_importantes = serializers.IntegerField()
    
    # Eficiencia
    tasa_deteccion = serializers.FloatField()
    tiempo_promedio_diagnostico = serializers.IntegerField()
    adherencia_tratamiento = serializers.FloatField()
    
    # Análisis poblacional
    poblacion_prioritaria = serializers.DictField()
    distribucion_edades = serializers.DictField()
    
    class Meta:
        fields = '__all__'


class DatosComparativosSerializer(serializers.Serializer):
    """
    Serializador para datos comparativos entre periodos
    """
    periodo_actual = serializers.DictField()
    periodo_anterior = serializers.DictField()
    variacion_absoluta = serializers.DictField()
    variacion_porcentual = serializers.DictField()
    
    class Meta:
        fields = '__all__'