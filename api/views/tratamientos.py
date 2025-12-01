# api/views/tratamientos.py
"""
Vistas para la API de tratamientos
Gestión completa con seguimiento temporal
"""
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import date, timedelta

from apps.tratamientos.models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from api.serializers.tratamientos import (
    TratamientoSerializer, 
    TratamientoListSerializer,
    EsquemaMedicamentoSerializer,
    DosisAdministradaSerializer
)
from api.permissions import EstablecimientoPermission, IsEnfermeraOrHigher

class TratamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de tratamientos
    """
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer
    permission_classes = [permissions.IsAuthenticated, EstablecimientoPermission, IsEnfermeraOrHigher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['esquema', 'resultado_final', 'paciente__establecimiento_salud']
    search_fields = ['paciente__nombre', 'paciente__rut', 'observaciones']
    ordering_fields = ['fecha_inicio', 'fecha_termino_estimada', 'fecha_registro']
    ordering = ['-fecha_inicio']
    
    def get_queryset(self):
        """
        Filtra tratamientos según acceso del usuario
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Prefetch relacionado para mejor performance
        queryset = queryset.select_related(
            'paciente', 'usuario_registro'
        ).prefetch_related('esquemas_medicamento')
        
        # Administradores ven todos
        if user.is_superuser or user.groups.filter(name='Administrador').exists():
            return queryset
        
        # Otros usuarios ven solo tratamientos de pacientes de su establecimiento
        if hasattr(user, 'perfilusuario') and user.perfilusuario.establecimiento:
            return queryset.filter(
                paciente__establecimiento_salud=user.perfilusuario.establecimiento
            )
        
        return queryset.none()
    
    def get_serializer_class(self):
        """
        Usa serializer simplificado para listados
        """
        if self.action == 'list':
            return TratamientoListSerializer
        return TratamientoSerializer
    
    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario que registra
        """
        serializer.save(usuario_registro=self.request.user)
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Lista solo tratamientos activos
        """
        queryset = self.get_queryset().filter(
            Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')
        )
        
        # Filtros adicionales
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_hasta)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TratamientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TratamientoListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos_a_terminar(self, request):
        """
        Tratamientos que terminan en los próximos 30 días
        """
        hoy = date.today()
        proximo_mes = hoy + timedelta(days=30)
        
        queryset = self.get_queryset().filter(
            fecha_termino_estimada__range=[hoy, proximo_mes],
            resultado_final__in=[None, 'En Tratamiento']
        ).order_by('fecha_termino_estimada')
        
        serializer = TratamientoListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """
        Estadísticas específicas de un tratamiento
        """
        tratamiento = self.get_object()
        
        # Obtener esquemas de medicamentos
        esquemas = tratamiento.esquemas_medicamento.all()
        
        # Calcular adherencia
        total_dosis = 0
        dosis_administradas = 0
        
        for esquema in esquemas:
            dosis = esquema.dosis_administradas.all()
            total_dosis += dosis.count()
            dosis_administradas += dosis.filter(administrada=True).count()
        
        adherencia = round((dosis_administradas / total_dosis * 100), 2) if total_dosis > 0 else 0
        
        estadisticas = {
            'id': tratamiento.id,
            'paciente': tratamiento.paciente.nombre,
            'esquema': tratamiento.get_esquema_display(),
            'dias_transcurridos': (date.today() - tratamiento.fecha_inicio).days,
            'dias_restantes': max((tratamiento.fecha_termino_estimada - date.today()).days, 0),
            'porcentaje_completado': tratamiento.porcentaje_completado,
            'total_medicamentos': esquemas.count(),
            'adherencia': f"{adherencia}%",
            'dosis_totales': total_dosis,
            'dosis_administradas': dosis_administradas,
            'dosis_pendientes': total_dosis - dosis_administradas,
            'esta_activo': tratamiento.esta_activo
        }
        
        return Response(estadisticas)
    
    @action(detail=True, methods=['post'])
    def agregar_medicamento(self, request, pk=None):
        """
        Agrega un medicamento al esquema de tratamiento
        """
        tratamiento = self.get_object()
        
        # Verificar que el tratamiento esté activo
        if not tratamiento.esta_activo:
            return Response(
                {'error': 'No se pueden agregar medicamentos a tratamientos finalizados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = EsquemaMedicamentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tratamiento=tratamiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_dosis(self, request, pk=None):
        """
        Registra administración de una dosis
        """
        tratamiento = self.get_object()
        
        # Buscar esquema de medicamento
        esquema_id = request.data.get('esquema_medicamento_id')
        try:
            esquema = EsquemaMedicamento.objects.get(id=esquema_id, tratamiento=tratamiento)
        except EsquemaMedicamento.DoesNotExist:
            return Response(
                {'error': 'Esquema de medicamento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Registrar dosis
        data = {
            'esquema_medicamento': esquema_id,
            'fecha_dosis': request.data.get('fecha_dosis', date.today()),
            'administrada': request.data.get('administrada', True),
            'hora_administracion': request.data.get('hora_administracion'),
            'observaciones': request.data.get('observaciones', ''),
            'usuario_administracion': request.user.id
        }
        
        serializer = DosisAdministradaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EsquemaMedicamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de esquemas de medicamentos
    """
    queryset = EsquemaMedicamento.objects.all()
    serializer_class = EsquemaMedicamentoSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnfermeraOrHigher]
    
    def get_queryset(self):
        """
        Filtra esquemas según tratamiento y acceso del usuario
        """
        queryset = super().get_queryset()
        
        # Filtrar por tratamiento si se especifica
        tratamiento_id = self.request.GET.get('tratamiento_id')
        if tratamiento_id:
            queryset = queryset.filter(tratamiento_id=tratamiento_id)
        
        return queryset.select_related('tratamiento', 'tratamiento__paciente')