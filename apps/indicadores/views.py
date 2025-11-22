from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from datetime import timedelta, datetime
import json
import csv

from .models import (
    IndicadoresCohorte,
    IndicadoresOperacionales,
    IndicadoresPrevencion,
    Alerta,
    Establecimiento,
    ReportePersonalizado
)
from .services import CalculadorIndicadores, GeneradorAlertas
from apps.pacientes.models import PacientesPaciente
from apps.tratamientos.models import Tratamiento
from apps.contactos.models import ContactosContacto

# Mixins de permisos para el módulo de indicadores
class PermisoIndicadoresMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'usuariosusuario'):
            return user.usuariosusuario.rol in ['medico', 'enfermera', 'tecnologo', 'admin']
        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "No tiene permisos para acceder al módulo de Indicadores.")
        return redirect('usuarios:dashboard')

class PermisoCohorteMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'usuariosusuario'):
            return user.usuariosusuario.rol in ['medico', 'admin']
        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "No tiene permisos para acceder a los Indicadores de Cohorte.")
        return redirect('indicadores:dashboard')

class PermisoOperacionalesMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'usuariosusuario'):
            return user.usuariosusuario.rol in ['medico', 'enfermera', 'admin']
        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "No tiene permisos para acceder a los Indicadores Operacionales.")
        return redirect('indicadores:dashboard')

class PermisoPrevencionMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'usuariosusuario'):
            return user.usuariosusuario.rol in ['enfermera', 'admin']
        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "No tiene permisos para acceder a los Indicadores de Prevención.")
        return redirect('indicadores:dashboard')

class PermisoReportesMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'usuariosusuario'):
            return user.usuariosusuario.rol in ['medico', 'admin']
        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "No tiene permisos para acceder a los Reportes Gerenciales.")
        return redirect('indicadores:dashboard')

class PermisoAdministradorMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'usuariosusuario'):
            return user.usuariosusuario.rol == 'admin' or getattr(user.usuariosusuario, 'es_administrador', False)
        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "No tiene permisos de administrador para esta acción.")
        return redirect('indicadores:dashboard')

# Vistas principales
class DashboardPrincipalView(PermisoIndicadoresMixin, LoginRequiredMixin, TemplateView):
    """Vista principal del dashboard con datos reales"""
    template_name = 'indicadores/dashboard_principal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcular indicadores actuales si no existen
        try:
            CalculadorIndicadores.calcular_todos_indicadores()
        except Exception as e:
            print(f"Error calculando indicadores: {e}")
        
        # Obtener datos reales
        total_pacientes = PacientesPaciente.objects.count()
        pacientes_activos = PacientesPaciente.objects.filter(estado='activo').count()
        tratamientos_activos = Tratamiento.objects.filter(
            Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')
        ).count()
        contactos_pendientes = ContactosContacto.objects.filter(
            estado_estudio='pendiente'
        ).count()

        # Obtener el primer establecimiento para los gráficos
        establecimiento = Establecimiento.objects.first()
        if not establecimiento:
            # Crear establecimiento por defecto si no existe
            establecimiento = Establecimiento.objects.create(
                nombre="Establecimiento Principal",
                codigo="EST001",
                tipo="Centro de Salud",
                region="Región Principal"
            )

        # Obtener datos para gráficos
        indicadores = IndicadoresCohorte.objects.filter(
            establecimiento=establecimiento
        ).order_by('año', 'trimestre')[:8]

        trimestres = []
        tasas_exito = []
        tasas_abandono = []

        for ind in indicadores:
            trimestres.append(f"{ind.año}-{ind.get_trimestre_display()}")
            tasas_exito.append(float(ind.exito_tratamiento_porcentaje))
            tasas_abandono.append(float(ind.tasa_abandono))

        # Si no hay datos, crear algunos de ejemplo basados en datos reales
        if not trimestres:
            # Usar datos reales para crear indicadores de ejemplo
            hoy = timezone.now()
            año_actual = hoy.year
            trimestre_actual = 'Q' + str((hoy.month - 1) // 3 + 1)
            
            # Calcular métricas reales para el ejemplo
            pacientes_total = PacientesPaciente.objects.count()
            pacientes_egresados = PacientesPaciente.objects.filter(estado='egresado').count()
            pacientes_abandono = PacientesPaciente.objects.filter(estado='abandono').count()
            
            exito_ejemplo = round((pacientes_egresados / pacientes_total * 100), 1) if pacientes_total > 0 else 85.0
            abandono_ejemplo = round((pacientes_abandono / pacientes_total * 100), 1) if pacientes_total > 0 else 3.5
            
            trimestres = [f'{año_actual}-Q1', f'{año_actual}-Q2', f'{año_actual}-Q3', f'{año_actual}-Q4']
            tasas_exito = [exito_ejemplo - 2, exito_ejemplo - 1, exito_ejemplo, exito_ejemplo + 1]
            tasas_abandono = [abandono_ejemplo + 1, abandono_ejemplo, abandono_ejemplo - 0.5, abandono_ejemplo]

        # Calcular éxito y abandono actual
        ultimo_trimestre = IndicadoresCohorte.objects.filter(
            establecimiento=establecimiento
        ).order_by('-año', '-trimestre').first()
        
        exito_actual = ultimo_trimestre.exito_tratamiento_porcentaje if ultimo_trimestre else tasas_exito[-1] if tasas_exito else 85.2
        abandono_actual = ultimo_trimestre.tasa_abandono if ultimo_trimestre else tasas_abandono[-1] if tasas_abandono else 3.8

        context.update({
            'trimestres': json.dumps(trimestres),
            'tasas_exito': json.dumps(tasas_exito),
            'tasas_abandono': json.dumps(tasas_abandono),
            'indicadores_cohorte': indicadores,
            'total_pacientes': total_pacientes,
            'pacientes_activos': pacientes_activos,
            'tratamientos_activos': tratamientos_activos,
            'contactos_pendientes': contactos_pendientes,
            'exito_actual': exito_actual,
            'abandono_actual': abandono_actual,
            'establecimiento_actual': establecimiento,
        })
        
        context['alertas_pendientes'] = Alerta.objects.filter(resuelta=False)[:5]
        context['total_establecimientos'] = Establecimiento.objects.count()
        context['total_indicadores'] = IndicadoresCohorte.objects.count()

        return context

class IndicadoresCohorteView(PermisoCohorteMixin, LoginRequiredMixin, ListView):
    """Vista para listar indicadores de cohorte"""
    model = IndicadoresCohorte
    template_name = 'indicadores/indicadores_cohorte.html'
    context_object_name = 'indicadores'
    paginate_by = 10

    def get_queryset(self):
        # Calcular indicadores actuales antes de mostrar
        try:
            CalculadorIndicadores.calcular_todos_indicadores()
        except Exception as e:
            print(f"Error calculando indicadores: {e}")
        
        # Filtrar por año si se especifica
        año = self.request.GET.get('anio')
        trimestre = self.request.GET.get('trimestre')
        
        queryset = IndicadoresCohorte.objects.all()
        
        if año and año != 'all':
            queryset = queryset.filter(año=int(año))
        
        if trimestre and trimestre != 'all':
            queryset = queryset.filter(trimestre=trimestre)
            
        return queryset.order_by('-año', '-trimestre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar años disponibles para el filtro
        años = IndicadoresCohorte.objects.values_list('año', flat=True).distinct().order_by('-año')
        context['años'] = años
        return context

class IndicadoresOperacionalesView(PermisoOperacionalesMixin, LoginRequiredMixin, ListView):
    """Vista para indicadores operacionales"""
    model = IndicadoresOperacionales
    template_name = 'indicadores/indicadores_operacionales.html'
    context_object_name = 'indicadores'
    paginate_by = 12

    def get_queryset(self):
        # Filtrar por año y mes si se especifica
        año = self.request.GET.get('anio')
        mes = self.request.GET.get('mes')
        
        queryset = IndicadoresOperacionales.objects.all()
        
        if año and año != 'all':
            queryset = queryset.filter(periodo__year=int(año))
        
        if mes and mes != 'all':
            queryset = queryset.filter(periodo__month=int(mes))
            
        return queryset.order_by('-periodo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar años disponibles para el filtro
        años = IndicadoresOperacionales.objects.dates('periodo', 'year', order='DESC')
        context['años'] = [date.year for date in años]
        return context

class IndicadoresPrevencionView(PermisoPrevencionMixin, LoginRequiredMixin, ListView):
    """Vista para indicadores de prevención"""
    model = IndicadoresPrevencion
    template_name = 'indicadores/indicadores_prevencion.html'
    context_object_name = 'indicadores'
    paginate_by = 12

    def get_queryset(self):
        # Filtrar por año y mes si se especifica
        año = self.request.GET.get('anio')
        mes = self.request.GET.get('mes')
        
        queryset = IndicadoresPrevencion.objects.all()
        
        if año and año != 'all':
            queryset = queryset.filter(periodo__year=int(año))
        
        if mes and mes != 'all':
            queryset = queryset.filter(periodo__month=int(mes))
            
        return queryset.order_by('-periodo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar años disponibles para el filtro
        años = IndicadoresPrevencion.objects.dates('periodo', 'year', order='DESC')
        context['años'] = [date.year for date in años]
        
        # Calcular promedios para las tarjetas de resumen
        if context['indicadores']:
            ultimo = context['indicadores'].first()
            context['cobertura_qp'] = ultimo.cobertura_quimioprofilaxis
            context['adherencia_qp'] = ultimo.adherencia_quimioprofilaxis
            context['cobertura_bcg'] = ultimo.cobertura_vacunacion_bcg
        else:
            context['cobertura_qp'] = 0
            context['adherencia_qp'] = 0
            context['cobertura_bcg'] = 0
            
        return context

class AlertasView(PermisoIndicadoresMixin, LoginRequiredMixin, ListView):
    """Vista para listar alertas"""
    model = Alerta
    template_name = 'indicadores/alertas_lista.html'
    context_object_name = 'alertas'
    paginate_by = 15

    def get_queryset(self):
        # Aplicar filtros si existen
        tipo = self.request.GET.get('tipo')
        nivel = self.request.GET.get('nivel')
        estado = self.request.GET.get('estado')
        establecimiento_id = self.request.GET.get('establecimiento')
        
        queryset = Alerta.objects.all()
        
        if tipo and tipo != 'all':
            queryset = queryset.filter(tipo=tipo)
            
        if nivel and nivel != 'all':
            queryset = queryset.filter(nivel=nivel)
            
        if estado == 'pendientes':
            queryset = queryset.filter(resuelta=False)
        elif estado == 'resueltas':
            queryset = queryset.filter(resuelta=True)
            
        if establecimiento_id and establecimiento_id != 'all':
            queryset = queryset.filter(establecimiento_id=establecimiento_id)
            
        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generar alertas antes de mostrar
        try:
            GeneradorAlertas.verificar_alertas_vencimientos()
            GeneradorAlertas.verificar_alertas_estudio_contactos()
        except Exception as e:
            print(f"Error generando alertas: {e}")

        # Estadísticas para el dashboard de alertas
        alertas = Alerta.objects.all()

        context.update({
            'alertas_criticas': alertas.filter(nivel='CRITICA', resuelta=False).count(),
            'alertas_altas': alertas.filter(nivel='ALTA', resuelta=False).count(),
            'alertas_pendientes': alertas.filter(resuelta=False).count(),
            'alertas_resueltas_7d': alertas.filter(
                resuelta=True,
                fecha_resolucion__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'establecimientos': Establecimiento.objects.all(),
            'usuarios': self.request.user.__class__.objects.filter(is_active=True),
            'tiempo_promedio_resolucion': self._calcular_tiempo_promedio_resolucion()
        })
        return context

    def _calcular_tiempo_promedio_resolucion(self):
        """Calcula el tiempo promedio de resolución de alertas"""
        alertas_resueltas = Alerta.objects.filter(
            resuelta=True,
            fecha_resolucion__isnull=False
        )
        if alertas_resueltas.exists():
            total_dias = 0
            for alerta in alertas_resueltas:
                if alerta.fecha_resolucion and alerta.fecha_creacion:
                    dias = (alerta.fecha_resolucion.date() - alerta.fecha_creacion.date()).days
                    total_dias += dias
            return round(total_dias / alertas_resueltas.count(), 1)
        return 0

class ReportesView(PermisoReportesMixin, LoginRequiredMixin, TemplateView):
    """Vista para reportes gerenciales"""
    template_name = 'indicadores/reportes_gerenciales.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reportes_personalizados'] = ReportePersonalizado.objects.filter(
            Q(compartido=True) | Q(usuario_creador=self.request.user)
        )
        
        # Estadísticas para los reportes predefinidos
        context['total_pacientes'] = PacientesPaciente.objects.count()
        context['total_tratamientos'] = Tratamiento.objects.count()
        context['total_contactos'] = ContactosContacto.objects.count()
        context['total_alertas'] = Alerta.objects.count()
        
        return context

class GenerarReporteCohorteView(PermisoReportesMixin, LoginRequiredMixin, View):
    """Vista para generar reportes de cohorte en CSV"""
    
    def get(self, request, *args, **kwargs):
        año = request.GET.get('año', datetime.now().year)
        trimestre = request.GET.get('trimestre', 'all')
        
        # Crear respuesta HTTP con archivo CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reporte_cohorte_{año}_{trimestre}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Año', 'Trimestre', 'Establecimiento', 'Casos Nuevos', 'Casos Retratamiento',
            'Total Casos', 'Curados', 'Abandonos', 'Fallecidos', 'Éxito Tratamiento %', 'Tasa Abandono %'
        ])
        
        # Filtrar datos
        queryset = IndicadoresCohorte.objects.filter(año=año)
        if trimestre != 'all':
            queryset = queryset.filter(trimestre=trimestre)
            
        for indicador in queryset:
            writer.writerow([
                indicador.año,
                indicador.get_trimestre_display(),
                indicador.establecimiento.nombre,
                indicador.casos_nuevos,
                indicador.casos_retratamiento,
                indicador.total_casos,
                indicador.curados,
                indicador.abandonos,
                indicador.fallecidos,
                indicador.exito_tratamiento_porcentaje,
                indicador.tasa_abandono
            ])
        
        return response

class GenerarReporteOperacionalView(PermisoReportesMixin, LoginRequiredMixin, View):
    """Vista para generar reportes operacionales en CSV"""
    
    def get(self, request, *args, **kwargs):
        año = request.GET.get('año', datetime.now().year)
        mes = request.GET.get('mes', 'all')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reporte_operacional_{año}_{mes}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Periodo', 'Establecimiento', 'Sintomáticos Respiratorios', 'Baciloscopias Realizadas',
            'Casos TB Encontrados', 'Contactos Identificados', 'Contactos Estudiados',
            'Pacientes TAES', 'Pacientes Adherentes', 'Índice Pesquisa %', 'Cobertura Contactos %', 'Adherencia TAES %'
        ])
        
        queryset = IndicadoresOperacionales.objects.filter(periodo__year=año)
        if mes != 'all':
            queryset = queryset.filter(periodo__month=mes)
            
        for indicador in queryset:
            writer.writerow([
                indicador.periodo.strftime("%Y-%m"),
                indicador.establecimiento.nombre,
                indicador.sintomaticos_respiratorios,
                indicador.baciloscopias_realizadas,
                indicador.casos_tb_encontrados,
                indicador.contactos_identificados,
                indicador.contactos_estudiados,
                indicador.pacientes_taes,
                indicador.pacientes_adherentes,
                indicador.indice_pesquisa,
                indicador.cobertura_estudio_contactos,
                indicador.adherencia_taes
            ])
        
        return response

class ActualizarIndicadoresView(PermisoAdministradorMixin, LoginRequiredMixin, View):
    """Vista para actualizar indicadores manualmente"""
    
    def post(self, request, *args, **kwargs):
        try:
            CalculadorIndicadores.calcular_todos_indicadores()
            return JsonResponse({'success': 'Indicadores actualizados correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ResolverAlertaView(LoginRequiredMixin, View):
    """Vista para resolver alertas"""
    
    def post(self, request, alerta_id):
        try:
            alerta = get_object_or_404(Alerta, id=alerta_id)
            # Verificar que el usuario tenga permisos para resolver esta alerta
            if (request.user == alerta.usuario_asignado or 
                request.user.is_superuser or 
                getattr(request.user.usuariosusuario, 'es_administrador', False)):
                
                alerta.resuelta = True
                alerta.fecha_resolucion = timezone.now()
                alerta.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'No tiene permisos para resolver esta alerta'}, status=403)
                
        except Alerta.DoesNotExist:
            return JsonResponse({'error': 'Alerta no encontrada'}, status=404)

class CrearAlertaView(LoginRequiredMixin, View):
    """Vista para crear alertas manualmente"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Solo administradores y superusuarios pueden crear alertas manualmente
            if not (request.user.is_superuser or getattr(request.user.usuariosusuario, 'es_administrador', False)):
                return JsonResponse({'error': 'No tiene permisos para crear alertas'}, status=403)
                
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            tipo = request.POST.get('tipo')
            nivel = request.POST.get('nivel')
            establecimiento_id = request.POST.get('establecimiento')
            usuario_asignado_id = request.POST.get('usuario_asignado')
            fecha_vencimiento = request.POST.get('fecha_vencimiento')
            
            # Validaciones básicas
            if not all([titulo, descripcion, tipo, nivel, establecimiento_id, fecha_vencimiento]):
                return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)
            
            establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
            usuario_asignado = None
            if usuario_asignado_id:
                usuario_asignado = get_object_or_404(request.user.__class__, id=usuario_asignado_id)
            
            alerta = Alerta.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                tipo=tipo,
                nivel=nivel,
                establecimiento=establecimiento,
                usuario_asignado=usuario_asignado,
                fecha_vencimiento=datetime.fromisoformat(fecha_vencimiento.replace('Z', '+00:00'))
            )
            
            return JsonResponse({'success': True, 'alerta_id': alerta.id})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class EliminarAlertaView(PermisoAdministradorMixin, LoginRequiredMixin, View):
    """Vista para eliminar alertas (solo administradores)"""
    
    def post(self, request, alerta_id):
        try:
            alerta = get_object_or_404(Alerta, id=alerta_id)
            alerta.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)