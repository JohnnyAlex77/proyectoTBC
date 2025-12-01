# api/serializers/tratamientos.py
"""
Serializadores para la API de tratamientos
Incluye campos calculados para seguimiento
"""
from rest_framework import serializers
from apps.tratamientos.models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from datetime import date

class EsquemaMedicamentoSerializer(serializers.ModelSerializer):
    """Serializador para esquemas de medicamentos"""
    
    medicamento_display = serializers.SerializerMethodField()
    frecuencia_display = serializers.SerializerMethodField()
    fase_display = serializers.SerializerMethodField()
    
    class Meta:
        model = EsquemaMedicamento
        fields = [
            'id', 'medicamento', 'medicamento_display', 'dosis_mg', 'frecuencia',
            'frecuencia_display', 'fase', 'fase_display', 'duracion_semanas',
            'fecha_inicio', 'fecha_termino'
        ]
    
    def get_medicamento_display(self, obj):
        """Obtiene display del medicamento"""
        return dict(obj.MEDICAMENTO_OPCIONES).get(obj.medicamento, obj.medicamento)
    
    def get_frecuencia_display(self, obj):
        """Obtiene display de la frecuencia"""
        return dict(obj.FRECUENCIA_OPCIONES).get(obj.frecuencia, obj.frecuencia)
    
    def get_fase_display(self, obj):
        """Obtiene display de la fase"""
        return dict(obj.FASES_OPCIONES).get(obj.fase, obj.fase)


class DosisAdministradaSerializer(serializers.ModelSerializer):
    """Serializador para dosis administradas"""
    
    class Meta:
        model = DosisAdministrada
        fields = [
            'id', 'esquema_medicamento', 'fecha_dosis', 'administrada',
            'hora_administracion', 'observaciones', 'usuario_administracion',
            'fecha_registro'
        ]
        read_only_fields = ['fecha_registro']


class TratamientoSerializer(serializers.ModelSerializer):
    """
    Serializador principal para tratamientos
    Incluye campos calculados y relaciones anidadas
    """
    esquema_display = serializers.SerializerMethodField()
    resultado_display = serializers.SerializerMethodField()
    duracion_dias = serializers.SerializerMethodField()
    esta_activo = serializers.SerializerMethodField()
    dias_transcurridos = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()
    porcentaje_completado = serializers.SerializerMethodField()
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)
    paciente_rut = serializers.CharField(source='paciente.rut', read_only=True)
    
    esquemas_medicamento = EsquemaMedicamentoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tratamiento
        fields = [
            'id', 'paciente', 'paciente_nombre', 'paciente_rut', 'esquema',
            'esquema_display', 'fecha_inicio', 'fecha_termino_estimada',
            'fecha_termino_real', 'peso_kg', 'resultado_final', 'resultado_display',
            'observaciones', 'duracion_dias', 'esta_activo', 'dias_transcurridos',
            'dias_restantes', 'porcentaje_completado', 'esquemas_medicamento',
            'usuario_registro', 'fecha_registro'
        ]
        read_only_fields = [
            'fecha_registro', 'usuario_registro', 'duracion_dias', 'esta_activo'
        ]
    
    def get_esquema_display(self, obj):
        """Obtiene display del esquema"""
        return obj.get_esquema_display()
    
    def get_resultado_display(self, obj):
        """Obtiene display del resultado"""
        if obj.resultado_final:
            return dict(obj.RESULTADO_OPCIONES).get(obj.resultado_final, obj.resultado_final)
        return None
    
    def get_duracion_dias(self, obj):
        """Calcula duración en días"""
        return obj.duracion_dias
    
    def get_esta_activo(self, obj):
        """Determina si el tratamiento está activo"""
        return obj.esta_activo
    
    def get_dias_transcurridos(self, obj):
        """Calcula días transcurridos desde inicio"""
        if obj.fecha_inicio:
            hoy = date.today()
            delta = hoy - obj.fecha_inicio
            return max(delta.days, 0)
        return 0
    
    def get_dias_restantes(self, obj):
        """Calcula días restantes hasta término"""
        if obj.fecha_inicio and obj.fecha_termino_estimada:
            hoy = date.today()
            if hoy > obj.fecha_termino_estimada:
                return 0
            delta = obj.fecha_termino_estimada - hoy
            return delta.days
        return None
    
    def get_porcentaje_completado(self, obj):
        """Calcula porcentaje completado del tratamiento"""
        if obj.fecha_inicio and obj.fecha_termino_estimada:
            total_dias = (obj.fecha_termino_estimada - obj.fecha_inicio).days
            dias_trans = self.get_dias_transcurridos(obj)
            if total_dias > 0:
                return min(round((dias_trans / total_dias) * 100, 2), 100)
        return 0
    
    def validate(self, data):
        """Valida consistencia de fechas"""
        fecha_inicio = data.get('fecha_inicio', getattr(self.instance, 'fecha_inicio', None))
        fecha_termino_estimada = data.get('fecha_termino_estimada', getattr(self.instance, 'fecha_termino_estimada', None))
        fecha_termino_real = data.get('fecha_termino_real', getattr(self.instance, 'fecha_termino_real', None))
        
        errors = {}
        
        # Validar que fecha término estimada sea después de inicio
        if fecha_inicio and fecha_termino_estimada and fecha_termino_estimada <= fecha_inicio:
            errors['fecha_termino_estimada'] = "La fecha término estimada debe ser posterior a la fecha de inicio"
        
        # Validar que fecha término real sea coherente
        if fecha_termino_real:
            if fecha_inicio and fecha_termino_real < fecha_inicio:
                errors['fecha_termino_real'] = "La fecha término real no puede ser anterior a la fecha de inicio"
            if fecha_termino_estimada and fecha_termino_real > fecha_termino_estimada:
                # Solo advertencia, no error
                data['observaciones'] = (data.get('observaciones', '') + 
                    f"\nNota: Tratamiento terminó después de la fecha estimada ({fecha_termino_real} > {fecha_termino_estimada})")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class TratamientoListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listados de tratamientos"""
    
    paciente_nombre = serializers.CharField(source='paciente.nombre')
    esta_activo = serializers.SerializerMethodField()
    
    class Meta:
        model = Tratamiento
        fields = [
            'id', 'paciente', 'paciente_nombre', 'esquema', 'fecha_inicio',
            'fecha_termino_estimada', 'resultado_final', 'esta_activo'
        ]
    
    def get_esta_activo(self, obj):
        return obj.esta_activo