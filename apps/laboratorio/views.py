from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import LaboratorioRedLaboratorios, LaboratorioControlCalidad, LaboratorioTarjetero, LaboratorioIndicadores
from .forms import LaboratorioForm, ControlCalidadForm, TarjeteroForm, IndicadoresForm

# Funciones auxiliares para control de acceso
def _tiene_acceso_laboratorio(user, laboratorio):
    """Verifica si el usuario tiene acceso al laboratorio específico"""
    if user.has_perm('laboratorio.view_all_laboratorios') or user.is_superuser:
        return True
        
    # Verificar acceso por establecimiento si el usuario tiene perfil
    if hasattr(user, 'usuariosusuario'):
        # En este caso, todos los usuarios autorizados pueden ver todos los laboratorios
        # pero se puede restringir por establecimiento si es necesario
        return True
        
    return False

def _filtrar_por_acceso(queryset, user):
    """Filtra el queryset según los permisos del usuario"""
    if not user.has_perm('laboratorio.view_all_laboratorios') and hasattr(user, 'usuariosusuario'):
        # Si no es administrador, aplicar filtros específicos
        rol = user.usuariosusuario.rol
        
        # Tecnólogos médicos ven todos los laboratorios
        if rol == 'tecnologo':
            return queryset
        
        # Otros roles pueden tener restricciones
        return queryset.filter(activo=True)
    
    return queryset

def _puede_crear_laboratorio(user):
    """Verifica si el usuario puede crear laboratorios"""
    return user.has_perm('laboratorio.add_laboratorioredlaboratorios') or user.is_superuser

def _puede_editar_laboratorio(user):
    """Verifica si el usuario puede editar laboratorios"""
    return user.has_perm('laboratorio.change_laboratorioredlaboratorios') or user.is_superuser

def _puede_eliminar_laboratorio(user):
    """Verifica si el usuario puede eliminar laboratorios"""
    return user.has_perm('laboratorio.delete_laboratorioredlaboratorios') or user.is_superuser

# Laboratorio Views
class LaboratorioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = LaboratorioRedLaboratorios
    template_name = 'laboratorio/laboratorios_lista.html'
    permission_required = 'laboratorio.view_laboratorioredlaboratorios'
    context_object_name = 'laboratorios'

    def get_queryset(self):
        queryset = LaboratorioRedLaboratorios.objects.filter(activo=True).order_by('nombre')
        return _filtrar_por_acceso(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = _puede_crear_laboratorio(self.request.user)
        context['puede_editar'] = _puede_editar_laboratorio(self.request.user)
        context['puede_eliminar'] = _puede_eliminar_laboratorio(self.request.user)
        return context

class LaboratorioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = LaboratorioRedLaboratorios
    form_class = LaboratorioForm
    template_name = 'laboratorio/laboratorio_form.html'
    permission_required = 'laboratorio.add_laboratorioredlaboratorios'
    success_url = reverse_lazy('laboratorio:laboratorios_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Laboratorio creado exitosamente.')
        return super().form_valid(form)

class LaboratorioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = LaboratorioRedLaboratorios
    form_class = LaboratorioForm
    template_name = 'laboratorio/laboratorio_form.html'
    permission_required = 'laboratorio.change_laboratorioredlaboratorios'
    success_url = reverse_lazy('laboratorio:laboratorios_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Laboratorio actualizado exitosamente.')
        return super().form_valid(form)

class LaboratorioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = LaboratorioRedLaboratorios
    template_name = 'laboratorio/laboratorio_confirm_delete.html'
    permission_required = 'laboratorio.delete_laboratorioredlaboratorios'
    success_url = reverse_lazy('laboratorio:laboratorios_lista')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Laboratorio eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class LaboratorioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = LaboratorioRedLaboratorios
    template_name = 'laboratorio/laboratorio_detalle.html'
    permission_required = 'laboratorio.view_laboratorioredlaboratorios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_editar'] = _puede_editar_laboratorio(self.request.user)
        context['puede_eliminar'] = _puede_eliminar_laboratorio(self.request.user)
        return context

# Control Calidad Views
class ControlCalidadListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = LaboratorioControlCalidad
    template_name = 'laboratorio/control_calidad_lista.html'
    permission_required = 'laboratorio.view_laboratoriocontrolcalidad'
    context_object_name = 'controles'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        laboratorio_id = self.request.GET.get('laboratorio')
        tipo_control = self.request.GET.get('tipo_control')

        if laboratorio_id:
            queryset = queryset.filter(laboratorio_id=laboratorio_id)
        if tipo_control:
            queryset = queryset.filter(tipo_control=tipo_control)

        queryset = _filtrar_por_acceso(queryset, self.request.user)
        return queryset.select_related('laboratorio', 'usuario_responsable').order_by('-fecha_control')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratorios'] = _filtrar_por_acceso(LaboratorioRedLaboratorios.objects.filter(activo=True), self.request.user)
        context['puede_crear'] = self.request.user.has_perm('laboratorio.add_laboratoriocontrolcalidad')
        context['puede_editar'] = self.request.user.has_perm('laboratorio.change_laboratoriocontrolcalidad')
        context['puede_eliminar'] = self.request.user.has_perm('laboratorio.delete_laboratoriocontrolcalidad')
        return context

class ControlCalidadCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = LaboratorioControlCalidad
    form_class = ControlCalidadForm
    template_name = 'laboratorio/control_calidad_form.html'
    permission_required = 'laboratorio.add_laboratoriocontrolcalidad'
    success_url = reverse_lazy('laboratorio:control_calidad_lista')

    def form_valid(self, form):
        form.instance.usuario_responsable = self.request.user
        messages.success(self.request, 'Control de calidad creado exitosamente.')
        return super().form_valid(form)

class ControlCalidadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = LaboratorioControlCalidad
    form_class = ControlCalidadForm
    template_name = 'laboratorio/control_calidad_form.html'
    permission_required = 'laboratorio.change_laboratoriocontrolcalidad'
    success_url = reverse_lazy('laboratorio:control_calidad_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Control de calidad actualizado exitosamente.')
        return super().form_valid(form)

class ControlCalidadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = LaboratorioControlCalidad
    template_name = 'laboratorio/control_calidad_confirm_delete.html'
    permission_required = 'laboratorio.delete_laboratoriocontrolcalidad'
    success_url = reverse_lazy('laboratorio:control_calidad_lista')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Control de calidad eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class ControlCalidadDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = LaboratorioControlCalidad
    template_name = 'laboratorio/control_calidad_detalle.html'
    permission_required = 'laboratorio.view_laboratoriocontrolcalidad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_editar'] = self.request.user.has_perm('laboratorio.change_laboratoriocontrolcalidad')
        context['puede_eliminar'] = self.request.user.has_perm('laboratorio.delete_laboratoriocontrolcalidad')
        return context

# Tarjetero Views
class TarjeteroListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = LaboratorioTarjetero
    template_name = 'laboratorio/tarjetero_lista.html'
    permission_required = 'laboratorio.view_laboratoriotarjetero'
    context_object_name = 'tarjeteros'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        laboratorio_id = self.request.GET.get('laboratorio')

        if fecha_desde:
            queryset = queryset.filter(fecha_deteccion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_deteccion__lte=fecha_hasta)
        if laboratorio_id:
            queryset = queryset.filter(laboratorio_referencia_id=laboratorio_id)

        queryset = _filtrar_por_acceso(queryset, self.request.user)
        return queryset.select_related('paciente', 'examen', 'laboratorio_referencia').order_by('-fecha_deteccion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratorios'] = _filtrar_por_acceso(LaboratorioRedLaboratorios.objects.filter(activo=True), self.request.user)
        context['puede_crear'] = self.request.user.has_perm('laboratorio.add_laboratoriotarjetero')
        context['puede_editar'] = self.request.user.has_perm('laboratorio.change_laboratoriotarjetero')
        context['puede_eliminar'] = self.request.user.has_perm('laboratorio.delete_laboratoriotarjetero')
        return context

class TarjeteroCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = LaboratorioTarjetero
    form_class = TarjeteroForm
    template_name = 'laboratorio/tarjetero_form.html'
    permission_required = 'laboratorio.add_laboratoriotarjetero'
    success_url = reverse_lazy('laboratorio:tarjetero_lista')

    def form_valid(self, form):
        form.instance.usuario_notificador = self.request.user
        messages.success(self.request, 'Registro de tarjetero creado exitosamente.')
        return super().form_valid(form)

class TarjeteroUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = LaboratorioTarjetero
    form_class = TarjeteroForm
    template_name = 'laboratorio/tarjetero_form.html'
    permission_required = 'laboratorio.change_laboratoriotarjetero'
    success_url = reverse_lazy('laboratorio:tarjetero_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Registro de tarjetero actualizado exitosamente.')
        return super().form_valid(form)

class TarjeteroDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = LaboratorioTarjetero
    template_name = 'laboratorio/tarjetero_confirm_delete.html'
    permission_required = 'laboratorio.delete_laboratoriotarjetero'
    success_url = reverse_lazy('laboratorio:tarjetero_lista')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Registro de tarjetero eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class TarjeteroDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = LaboratorioTarjetero
    template_name = 'laboratorio/tarjetero_detalle.html'
    permission_required = 'laboratorio.view_laboratoriotarjetero'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_editar'] = self.request.user.has_perm('laboratorio.change_laboratoriotarjetero')
        context['puede_eliminar'] = self.request.user.has_perm('laboratorio.delete_laboratoriotarjetero')
        return context

# Indicadores Views
class IndicadoresListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = LaboratorioIndicadores
    template_name = 'laboratorio/indicadores_lista.html'
    permission_required = 'laboratorio.view_laboratorioindicadores'
    context_object_name = 'indicadores'

    def get_queryset(self):
        queryset = super().get_queryset()
        periodo = self.request.GET.get('periodo')
        laboratorio_id = self.request.GET.get('laboratorio')

        if periodo:
            queryset = queryset.filter(periodo=periodo)
        if laboratorio_id:
            queryset = queryset.filter(laboratorio_id=laboratorio_id)

        queryset = _filtrar_por_acceso(queryset, self.request.user)
        return queryset.select_related('laboratorio').order_by('-periodo', 'laboratorio__nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        indicadores = context['indicadores']
        
        # Cálculos para el resumen
        if indicadores:
            context['total_muestras_recibidas'] = sum(i.muestras_recibidas for i in indicadores)
            context['total_muestras_procesadas'] = sum(i.muestras_procesadas for i in indicadores)
            context['total_positivos'] = sum(i.positivos for i in indicadores)
            context['promedio_contaminacion'] = sum(i.contaminacion_porcentaje for i in indicadores) / len(indicadores)
            context['promedio_tiempo_respuesta'] = sum(i.tiempo_respuesta_promedio for i in indicadores) / len(indicadores)
            context['tasa_positividad'] = (context['total_positivos'] / context['total_muestras_procesadas'] * 100) if context['total_muestras_procesadas'] > 0 else 0
        else:
            context.update({
                'total_muestras_recibidas': 0,
                'total_muestras_procesadas': 0,
                'total_positivos': 0,
                'promedio_contaminacion': 0,
                'promedio_tiempo_respuesta': 0,
                'tasa_positividad': 0
            })
        
        context['laboratorios'] = _filtrar_por_acceso(LaboratorioRedLaboratorios.objects.filter(activo=True), self.request.user)
        context['puede_crear'] = self.request.user.has_perm('laboratorio.add_laboratorioindicadores')
        context['puede_editar'] = self.request.user.has_perm('laboratorio.change_laboratorioindicadores')
        context['puede_eliminar'] = self.request.user.has_perm('laboratorio.delete_laboratorioindicadores')
        return context

class IndicadoresCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = LaboratorioIndicadores
    form_class = IndicadoresForm
    template_name = 'laboratorio/indicadores_form.html'
    permission_required = 'laboratorio.add_laboratorioindicadores'
    success_url = reverse_lazy('laboratorio:indicadores_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Indicadores creados exitosamente.')
        return super().form_valid(form)

class IndicadoresUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = LaboratorioIndicadores
    form_class = IndicadoresForm
    template_name = 'laboratorio/indicadores_form.html'
    permission_required = 'laboratorio.change_laboratorioindicadores'
    success_url = reverse_lazy('laboratorio:indicadores_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Indicadores actualizados exitosamente.')
        return super().form_valid(form)

class IndicadoresDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = LaboratorioIndicadores
    template_name = 'laboratorio/indicadores_confirm_delete.html'
    permission_required = 'laboratorio.delete_laboratorioindicadores'
    success_url = reverse_lazy('laboratorio:indicadores_lista')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Indicadores eliminados exitosamente.')
        return super().delete(request, *args, **kwargs)

# Dashboard y Reportes
class DashboardLaboratorioView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'laboratorio/dashboard.html'
    permission_required = 'laboratorio.view_laboratorioredlaboratorios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas para el dashboard
        context['total_laboratorios'] = _filtrar_por_acceso(LaboratorioRedLaboratorios.objects.filter(activo=True), self.request.user).count()
        context['controles_mes'] = _filtrar_por_acceso(LaboratorioControlCalidad.objects.filter(
            fecha_control__month=timezone.now().month,
            fecha_control__year=timezone.now().year
        ), self.request.user).count()
        context['positivos_mes'] = _filtrar_por_acceso(LaboratorioTarjetero.objects.filter(
            fecha_deteccion__month=timezone.now().month,
            fecha_deteccion__year=timezone.now().year
        ), self.request.user).count()

        # Controles por resultado
        context['controles_satisfactorios'] = _filtrar_por_acceso(LaboratorioControlCalidad.objects.filter(
            resultado='satisfactorio'
        ), self.request.user).count()
        context['controles_insatisfactorios'] = _filtrar_por_acceso(LaboratorioControlCalidad.objects.filter(
            resultado='insatisfactorio'
        ), self.request.user).count()

        # Últimos controles
        context['ultimos_controles'] = _filtrar_por_acceso(LaboratorioControlCalidad.objects.select_related(
            'laboratorio', 'usuario_responsable'
        ), self.request.user).order_by('-fecha_control')[:5]

        # Últimos positivos
        context['ultimos_positivos'] = _filtrar_por_acceso(LaboratorioTarjetero.objects.select_related(
            'paciente', 'laboratorio_referencia'
        ), self.request.user).order_by('-fecha_deteccion')[:5]

        # Laboratorios para filtros
        context['laboratorios'] = _filtrar_por_acceso(LaboratorioRedLaboratorios.objects.filter(activo=True), self.request.user)

        return context

class ReportesLaboratorioView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'laboratorio/reportes.html'
    permission_required = 'laboratorio.view_laboratorioredlaboratorios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratorios'] = _filtrar_por_acceso(LaboratorioRedLaboratorios.objects.filter(activo=True), self.request.user)
        context['total_laboratorios'] = context['laboratorios'].count()
        context['total_controles'] = _filtrar_por_acceso(LaboratorioControlCalidad.objects.all(), self.request.user).count()
        context['total_tarjetero'] = _filtrar_por_acceso(LaboratorioTarjetero.objects.all(), self.request.user).count()
        context['total_indicadores'] = _filtrar_por_acceso(LaboratorioIndicadores.objects.all(), self.request.user).count()
        return context