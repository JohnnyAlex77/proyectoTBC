# api/views/dashboard.py
"""
Vistas para el dashboard del sistema TBC
Proporciona métricas clave y estadísticas
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Count, Q, Avg, Max, Min
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone
from datetime import date, timedelta
import statistics

from apps.pacientes.models import PacientesPaciente
from apps.tratamientos.models import Tratamiento
from apps.examenes.models import ExamenesExamenbacteriologico
from apps.contactos.models import ContactosContacto
from apps.prevencion.models import PrevencionQuimioprofilaxis
from apps.laboratorio.models import LaboratorioRedLaboratorios

class DashboardEstadisticasView(APIView):
    """
    Vista para estadísticas generales del dashboard
    Retorna métricas clave del sistema TBC
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retorna estadísticas generales filtradas por acceso del usuario
        """
        user = request.user
        
        # Determinar filtro de establecimiento
        establecimiento_filtro = Q()
        if not (user.is_superuser or user.groups.filter(name='Administrador').exists()):
            if hasattr(user, 'perfilusuario') and user.perfilusuario.establecimiento:
                establecimiento = user.perfilusuario.establecimiento
                establecimiento_filtro = Q(establecimiento_salud=establecimiento)
        
        # Pacientes
        pacientes = PacientesPaciente.objects.filter(establecimiento_filtro)
        total_pacientes = pacientes.count()
        
        # Estadísticas de pacientes
        pacientes_estadisticas = {
            'total': total_pacientes,
            'por_estado': list(pacientes.values('estado').annotate(total=Count('id'))),
            'por_tipo_tbc': list(pacientes.values('tipo_tbc').annotate(total=Count('id'))),
            'por_sexo': list(pacientes.values('sexo').annotate(total=Count('id'))),
            'nuevos_ultimo_mes': pacientes.filter(
                fecha_registro__date__gte=date.today() - timedelta(days=30)
            ).count()
        }
        
        # Tratamientos (filtrando por establecimiento a través del paciente)
        tratamientos = Tratamiento.objects.filter(
            paciente__establecimiento_salud__in=[est.establecimiento_salud 
               for est in pacientes.values('establecimiento_salud').distinct()]
        ) if establecimiento_filtro else Tratamiento.objects.all()
        
        tratamientos_estadisticas = {
            'total': tratamientos.count(),
            'activos': tratamientos.filter(
                Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')
            ).count(),
            'completados': tratamientos.filter(resultado_final='Curación').count(),
            'abandonados': tratamientos.filter(resultado_final='Abandono').count(),
            'por_esquema': list(tratamientos.values('esquema').annotate(total=Count('id')))
        }
        
        # Exámenes
        examenes = ExamenesExamenbacteriologico.objects.filter(
            paciente__establecimiento_salud__in=[est.establecimiento_salud 
               for est in pacientes.values('establecimiento_salud').distinct()]
        ) if establecimiento_filtro else ExamenesExamenbacteriologico.objects.all()
        
        examenes_estadisticas = {
            'total': examenes.count(),
            'positivos': examenes.filter(resultado='POSITIVO').count(),
            'negativos': examenes.filter(resultado='NEGATIVO').count(),
            'pendientes': examenes.filter(resultado='PENDIENTE').count(),
            'por_tipo': list(examenes.values('tipo_examen').annotate(total=Count('id')))
        }
        
        # Contactos
        contactos = ContactosContacto.objects.filter(
            paciente_indice__establecimiento_salud__in=[est.establecimiento_salud 
               for est in pacientes.values('establecimiento_salud').distinct()]
        ) if establecimiento_filtro else ContactosContacto.objects.all()
        
        contactos_estadisticas = {
            'total': contactos.count(),
            'estudiados': contactos.filter(estado_estudio='completado').count(),
            'pendientes': contactos.filter(estado_estudio='pendiente').count(),
            'por_parentesco': list(contactos.values('parentesco').annotate(total=Count('id')))
        }
        
        # Prevención
        prevencion = PrevencionQuimioprofilaxis.objects.all()
        # Filtrar por acceso si es necesario
        
        prevencion_estadisticas = {
            'total': prevencion.count(),
            'activos': prevencion.filter(estado='en_curso').count(),
            'completados': prevencion.filter(estado='completado').count()
        }
        
        # Laboratorios
        laboratorios = LaboratorioRedLaboratorios.objects.filter(activo=True)
        
        # Construir respuesta consolidada
        data = {
            'pacientes': pacientes_estadisticas,
            'tratamientos': tratamientos_estadisticas,
            'examenes': examenes_estadisticas,
            'contactos': contactos_estadisticas,
            'prevencion': prevencion_estadisticas,
            'laboratorios': {
                'total': laboratorios.count(),
                'activos': laboratorios.count()
            },
            'actualizado': timezone.now().isoformat(),
            'periodo': {
                'desde': (date.today() - timedelta(days=365)).isoformat(),
                'hasta': date.today().isoformat()
            }
        }
        
        return Response(data)


class DashboardTendenciasView(APIView):
    """
    Vista para análisis de tendencias temporales
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retorna datos de tendencias mensuales/anuales
        """
        # Obtener parámetros de periodo
        periodo = request.GET.get('periodo', 'mensual')  # mensual, anual
        meses = int(request.GET.get('meses', 12))
        
        fecha_inicio = date.today() - timedelta(days=30*meses)
        
        # Preparar datos de tendencias
        tendencias = {
            'pacientes': self._tendencia_pacientes(fecha_inicio, periodo),
            'tratamientos': self._tendencia_tratamientos(fecha_inicio, periodo),
            'examenes': self._tendencia_examenes(fecha_inicio, periodo)
        }
        
        return Response(tendencias)
    
    def _tendencia_pacientes(self, fecha_inicio, periodo):
        """Genera tendencia de pacientes por periodo"""
        pacientes = PacientesPaciente.objects.filter(
            fecha_registro__date__gte=fecha_inicio
        )
        
        if periodo == 'mensual':
            pacientes_tendencia = pacientes.annotate(
                periodo=TruncMonth('fecha_registro')
            ).values('periodo').annotate(
                total=Count('id'),
                nuevos=Count('id', filter=Q(fecha_diagnostico__isnull=False))
            ).order_by('periodo')
        else:  # anual
            pacientes_tendencia = pacientes.annotate(
                periodo=TruncYear('fecha_registro')
            ).values('periodo').annotate(
                total=Count('id'),
                nuevos=Count('id', filter=Q(fecha_diagnostico__isnull=False))
            ).order_by('periodo')
        
        return list(pacientes_tendencia)
    
    def _tendencia_tratamientos(self, fecha_inicio, periodo):
        """Genera tendencia de tratamientos por periodo"""
        tratamientos = Tratamiento.objects.filter(
            fecha_inicio__gte=fecha_inicio
        )
        
        if periodo == 'mensual':
            tendencia = tratamientos.annotate(
                periodo=TruncMonth('fecha_inicio')
            ).values('periodo').annotate(
                total=Count('id'),
                activos=Count('id', filter=Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')),
                exitosos=Count('id', filter=Q(resultado_final='Curación'))
            ).order_by('periodo')
        else:
            tendencia = tratamientos.annotate(
                periodo=TruncYear('fecha_inicio')
            ).values('periodo').annotate(
                total=Count('id'),
                activos=Count('id', filter=Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')),
                exitosos=Count('id', filter=Q(resultado_final='Curación'))
            ).order_by('periodo')
        
        return list(tendencia)
    
    def _tendencia_examenes(self, fecha_inicio, periodo):
        """Genera tendencia de exámenes por periodo"""
        examenes = ExamenesExamenbacteriologico.objects.filter(
            fecha_toma_muestra__gte=fecha_inicio
        )
        
        if periodo == 'mensual':
            tendencia = examenes.annotate(
                periodo=TruncMonth('fecha_toma_muestra')
            ).values('periodo').annotate(
                total=Count('id'),
                positivos=Count('id', filter=Q(resultado='POSITIVO')),
                pendientes=Count('id', filter=Q(resultado='PENDIENTE'))
            ).order_by('periodo')
        else:
            tendencia = examenes.annotate(
                periodo=TruncYear('fecha_toma_muestra')
            ).values('periodo').annotate(
                total=Count('id'),
                positivos=Count('id', filter=Q(resultado='POSITIVO')),
                pendientes=Count('id', filter=Q(resultado='PENDIENTE'))
            ).order_by('periodo')
        
        return list(tendencia)


class DashboardAlertasView(APIView):
    """
    Vista para alertas y notificaciones del sistema
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retorna alertas activas del sistema
        """
        alertas = []
        hoy = date.today()
        
        # Alertas de tratamientos próximos a terminar
        tratamientos_proximos = Tratamiento.objects.filter(
            fecha_termino_estimada__range=[hoy, hoy + timedelta(days=7)],
            resultado_final__in=[None, 'En Tratamiento']
        )
        
        for tratamiento in tratamientos_proximos:
            dias_restantes = (tratamiento.fecha_termino_estimada - hoy).days
            alertas.append({
                'tipo': 'tratamiento',
                'nivel': 'info' if dias_restantes > 3 else 'warning',
                'mensaje': f"Tratamiento de {tratamiento.paciente.nombre} finaliza en {dias_restantes} días",
                'fecha': tratamiento.fecha_termino_estimada,
                'url': f"/tratamientos/{tratamiento.id}/"
            })
        
        # Alertas de exámenes pendientes (más de 7 días)
        examenes_pendientes = ExamenesExamenbacteriologico.objects.filter(
            resultado='PENDIENTE',
            fecha_toma_muestra__lte=hoy - timedelta(days=7)
        )
        
        for examen in examenes_pendientes:
            dias_pendiente = (hoy - examen.fecha_toma_muestra).days
            alertas.append({
                'tipo': 'examen',
                'nivel': 'warning' if dias_pendiente <= 14 else 'danger',
                'mensaje': f"Examen {examen.get_tipo_examen_display()} de {examen.paciente.nombre} pendiente por {dias_pendiente} días",
                'fecha': examen.fecha_toma_muestra,
                'url': f"/examenes/{examen.id}/"
            })
        
        # Alertas de quimioprofilaxis vencida
        quimio_vencida = PrevencionQuimioprofilaxis.objects.filter(
            estado='en_curso',
            fecha_termino_prevista__lt=hoy
        )
        
        for quimio in quimio_vencida:
            dias_vencida = (hoy - quimio.fecha_termino_prevista).days
            alertas.append({
                'tipo': 'prevencion',
                'nivel': 'warning',
                'mensaje': f"Quimioprofilaxis de {quimio.get_nombre_paciente_contacto()} vencida hace {dias_vencida} días",
                'fecha': quimio.fecha_termino_prevista,
                'url': f"/prevencion/quimioprofilaxis/{quimio.id}/"
            })
        
        # Ordenar alertas por nivel de prioridad
        nivel_prioridad = {'danger': 0, 'warning': 1, 'info': 2}
        alertas.sort(key=lambda x: nivel_prioridad.get(x['nivel'], 3))
        
        return Response({
            'total': len(alertas),
            'alertas': alertas[:20],  # Limitar a 20 alertas
            'actualizado': timezone.now().isoformat()
        })