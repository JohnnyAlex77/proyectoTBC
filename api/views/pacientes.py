# api/views/pacientes.py
"""
Vistas para la API de pacientes
Implementan CRUD completo con control de acceso por establecimiento
"""
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import date, timedelta
from django.utils import timezone

from apps.pacientes.models import PacientesPaciente
from api.serializers.pacientes import PacienteSerializer, PacienteListSerializer
from api.permissions import EstablecimientoPermission, IsEnfermeraOrHigher

class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de pacientes
    Permite CRUD con filtrado, búsqueda y ordenamiento
    """
    queryset = PacientesPaciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated, EstablecimientoPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'estado', 'tipo_tbc', 'comuna', 'establecimiento_salud',
        'sexo', 'poblacion_prioritaria'
    ]
    search_fields = ['nombre', 'rut', 'comuna', 'domicilio', 'telefono']
    ordering_fields = [
        'nombre', 'fecha_nacimiento', 'fecha_diagnostico', 'fecha_registro'
    ]
    ordering = ['-fecha_registro']
    
    def get_queryset(self):
        """
        Filtra pacientes según el establecimiento del usuario
        Administradores ven todos, otros usuarios solo su establecimiento
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todos los pacientes
        if user.is_superuser or user.groups.filter(name='Administrador').exists():
            return queryset.select_related('usuario_registro')
        
        # Otros usuarios ven solo pacientes de su establecimiento
        if hasattr(user, 'perfilusuario') and user.perfilusuario.establecimiento:
            return queryset.filter(
                establecimiento_salud=user.perfilusuario.establecimiento
            ).select_related('usuario_registro')
        
        return queryset.none()
    
    def get_serializer_class(self):
        """
        Usa serializer simplificado para listados, completo para detalle
        """
        if self.action == 'list':
            return PacienteListSerializer
        return PacienteSerializer
    
    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario que registra
        """
        serializer.save(usuario_registro=self.request.user)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para estadísticas de pacientes
        Retorna conteos por estado, tipo TBC y más
        """
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        estadisticas = {
            'total': queryset.count(),
            'por_sexo': list(queryset.values('sexo').annotate(total=Count('id'))),
            'por_estado': list(queryset.values('estado').annotate(total=Count('id'))),
            'por_tipo_tbc': list(queryset.values('tipo_tbc').annotate(total=Count('id'))),
            'por_comuna': list(queryset.values('comuna').annotate(total=Count('id')).order_by('-total')[:10]),
            'por_poblacion_prioritaria': list(queryset.exclude(poblacion_prioritaria='').values(
                'poblacion_prioritaria').annotate(total=Count('id')))
        }
        
        # Estadísticas temporales
        ultimo_mes = timezone.now().date() - timedelta(days=30)
        estadisticas['nuevos_ultimo_mes'] = queryset.filter(
            fecha_registro__date__gte=ultimo_mes
        ).count()
        
        # Edad promedio
        pacientes_con_edad = queryset.exclude(fecha_nacimiento=None)
        if pacientes_con_edad.exists():
            edades = [p.get_edad() for p in pacientes_con_edad if p.get_edad() is not None]
            if edades:
                estadisticas['edad_promedio'] = round(sum(edades) / len(edades), 1)
                estadisticas['edad_minima'] = min(edades)
                estadisticas['edad_maxima'] = max(edades)
        
        return Response(estadisticas)
    
    @action(detail=False, methods=['get'])
    def busqueda_avanzada(self, request):
        """
        Búsqueda avanzada con múltiples parámetros
        """
        queryset = self.get_queryset()
        
        # Parámetros de búsqueda
        nombre = request.GET.get('nombre', '')
        comuna = request.GET.get('comuna', '')
        edad_min = request.GET.get('edad_min')
        edad_max = request.GET.get('edad_max')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        # Aplicar filtros
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if comuna:
            queryset = queryset.filter(comuna__icontains=comuna)
        
        # Filtrar por edad
        if edad_min or edad_max:
            hoy = date.today()
            if edad_min:
                fecha_max_nac = hoy.replace(year=hoy.year - int(edad_min))
                queryset = queryset.filter(fecha_nacimiento__lte=fecha_max_nac)
            if edad_max:
                fecha_min_nac = hoy.replace(year=hoy.year - int(edad_max) - 1)
                queryset = queryset.filter(fecha_nacimiento__gte=fecha_min_nac)
        
        # Filtrar por fecha de diagnóstico
        if fecha_desde:
            queryset = queryset.filter(fecha_diagnostico__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_diagnostico__lte=fecha_hasta)
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PacienteListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PacienteListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tratamientos(self, request, pk=None):
        """
        Obtiene tratamientos de un paciente específico
        """
        paciente = self.get_object()
        
        # Import aquí para evitar import circular
        try:
            from apps.tratamientos.models import Tratamiento
            tratamientos = Tratamiento.objects.filter(paciente=paciente)
            
            from api.serializers.tratamientos import TratamientoListSerializer
            serializer = TratamientoListSerializer(tratamientos, many=True)
            return Response(serializer.data)
        except ImportError:
            return Response({'error': 'Módulo de tratamientos no disponible'}, 
                          status=status.HTTP_501_NOT_IMPLEMENTED)
    
    @action(detail=True, methods=['get'])
    def examenes(self, request, pk=None):
        """
        Obtiene exámenes de un paciente específico
        """
        paciente = self.get_object()
        
        try:
            # Import aquí para evitar import circular
            from apps.examenes.models import ExamenesExamenbacteriologico
            
            examenes = ExamenesExamenbacteriologico.objects.filter(paciente=paciente)
            
            # Serializar exámenes simplificados - CORRECCIÓN DEL ERROR PYLANCE
            examenes_data = []
            for examen in examenes:
                # Usar pk en lugar de id para compatibilidad con Pylance
                examen_id = examen.pk if hasattr(examen, 'pk') else getattr(examen, 'id', None)
                
                examenes_data.append({
                    'id': examen_id,
                    'tipo_examen': examen.get_tipo_examen_display(),
                    'fecha_toma_muestra': examen.fecha_toma_muestra,
                    'resultado': examen.get_resultado_display(),
                    'estado_examen': examen.get_estado_examen_display()
                })
            
            return Response(examenes_data)
            
        except ImportError:
            return Response({'error': 'Módulo de exámenes no disponible'}, 
                          status=status.HTTP_501_NOT_IMPLEMENTED)