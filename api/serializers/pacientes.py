# api/serializers/pacientes.py
"""
Serializadores para la API de pacientes
Transforman modelos en JSON y viceversa
"""
from rest_framework import serializers
from apps.pacientes.models import PacientesPaciente
from datetime import date

class PacienteSerializer(serializers.ModelSerializer):
    """
    Serializador principal para pacientes
    Incluye campos calculados y relaciones
    """
    edad = serializers.SerializerMethodField()
    sexo_display = serializers.SerializerMethodField()
    tipo_tbc_display = serializers.SerializerMethodField()
    estado_display = serializers.SerializerMethodField()
    poblacion_prioritaria_display = serializers.SerializerMethodField()
    enfermedades_list = serializers.SerializerMethodField()
    alergias_list = serializers.SerializerMethodField()
    rut_formateado = serializers.SerializerMethodField()
    tiene_tratamiento_activo = serializers.SerializerMethodField()
    
    class Meta:
        model = PacientesPaciente
        fields = [
            'id', 'rut', 'rut_formateado', 'nombre', 'fecha_nacimiento', 'edad',
            'sexo', 'sexo_display', 'domicilio', 'comuna', 'telefono',
            'establecimiento_salud', 'fecha_diagnostico', 'tipo_tbc', 'tipo_tbc_display',
            'baciloscopia_inicial', 'cultivo_inicial', 'poblacion_prioritaria',
            'poblacion_prioritaria_display', 'enfermedades_preexistentes',
            'enfermedades_list', 'alergias', 'alergias_list', 'estado', 'estado_display',
            'fecha_registro', 'usuario_registro', 'tiene_tratamiento_activo'
        ]
        read_only_fields = [
            'fecha_registro', 'usuario_registro', 'edad', 'tiene_tratamiento_activo'
        ]
    
    def get_edad(self, obj):
        """Calcula la edad del paciente a partir de la fecha de nacimiento"""
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return None
    
    def get_sexo_display(self, obj):
        """Obtiene el texto descriptivo para el sexo"""
        return obj.get_sexo_display()
    
    def get_tipo_tbc_display(self, obj):
        """Obtiene el texto descriptivo para el tipo de TBC"""
        return obj.get_tipo_tbc_display()
    
    def get_estado_display(self, obj):
        """Obtiene el texto descriptivo para el estado"""
        return obj.get_estado_display()
    
    def get_poblacion_prioritaria_display(self, obj):
        """Obtiene el texto descriptivo para población prioritaria"""
        return obj.get_poblacion_prioritaria_display()
    
    def get_enfermedades_list(self, obj):
        """Convierte enfermedades a lista"""
        return obj.get_enfermedades_list()
    
    def get_alergias_list(self, obj):
        """Convierte alergias a lista"""
        return obj.get_alergias_list()
    
    def get_rut_formateado(self, obj):
        """Devuelve el RUT formateado con puntos"""
        return obj.get_rut_formateado()
    
    def get_tiene_tratamiento_activo(self, obj):
        """Verifica si el paciente tiene tratamiento activo"""
        return obj.tiene_tratamiento_activo()
    
    def validate_rut(self, value):
        """Valida que el RUT sea único en el sistema"""
        if self.instance and self.instance.rut == value:
            return value
        
        if PacientesPaciente.objects.filter(rut=value).exists():
            raise serializers.ValidationError("Este RUT ya está registrado en el sistema")
        return value
    
    def validate_fecha_nacimiento(self, value):
        """Valida que la fecha de nacimiento sea lógica"""
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura")
        return value
    
    def validate_fecha_diagnostico(self, value):
        """Valida que la fecha de diagnóstico sea lógica"""
        if value and value > date.today():
            raise serializers.ValidationError("La fecha de diagnóstico no puede ser futura")
        return value


class PacienteListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listados de pacientes
    Optimizado para rendimiento en listados
    """
    edad = serializers.SerializerMethodField()
    
    class Meta:
        model = PacientesPaciente
        fields = [
            'id', 'rut', 'nombre', 'edad', 'sexo', 'comuna',
            'establecimiento_salud', 'tipo_tbc', 'estado', 'fecha_diagnostico'
        ]
    
    def get_edad(self, obj):
        """Calcula edad simplificada"""
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year
        return None
    
    