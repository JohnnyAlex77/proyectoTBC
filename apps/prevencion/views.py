from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import PrevencionQuimioprofilaxis, PrevencionVacunacionBCG, PrevencionSeguimiento
from .forms import QuimioprofilaxisForm, VacunacionBCGForm, SeguimientoForm

# Importaciones para las funciones AJAX
from apps.pacientes.models import PacientesPaciente
from apps.contactos.models import ContactosContacto


# =============================================================================
# FUNCIONES AUXILIARES PARA CONTROL DE ACCESO
# =============================================================================

def _tiene_acceso_prevencion(user, objeto=None):
    """
    Verifica si el usuario tiene acceso a los módulos de prevención
    según su rol y establecimiento
    """
    # Superusuarios y administradores tienen acceso completo
    if user.is_superuser or _es_administrador(user):
        return True
    
    # Verificar permisos específicos por rol
    if _tiene_perfil_usuario(user):
        rol = _obtener_rol_usuario(user)
        
        # Enfermeras y paramédicos tienen acceso completo a prevención
        if rol in ['enfermera', 'paramedico']:
            return True
        
        # Médicos pueden ver pero no modificar
        if rol == 'medico' and user.has_perm('prevencion.view_quimioprofilaxis'):
            return True
        
        # Tecnólogos no tienen acceso a prevención
        if rol == 'tecnologo':
            return False
    
    return False


def _filtrar_por_establecimiento(queryset, user, tipo='quimioprofilaxis'):
    """
    Filtra el queryset por establecimiento si el usuario no es administrador
    """
    if not _tiene_acceso_prevencion(user):
        return queryset.none()
    
    # Administradores ven todo
    if user.is_superuser or _es_administrador(user):
        return queryset
    
    # Filtrar por establecimiento del usuario
    establecimiento = _obtener_establecimiento_usuario(user)
    if establecimiento:
        if tipo == 'quimioprofilaxis':
            return queryset.filter(
                Q(paciente__establecimiento_salud=establecimiento) |
                Q(contacto__paciente_indice__establecimiento_salud=establecimiento)
            )
        elif tipo == 'vacunacion':
            return queryset.filter(paciente__establecimiento_salud=establecimiento)
        elif tipo == 'seguimiento':
            return queryset.filter(
                Q(quimioprofilaxis__paciente__establecimiento_salud=establecimiento) |
                Q(quimioprofilaxis__contacto__paciente_indice__establecimiento_salud=establecimiento) |
                Q(vacunacion__paciente__establecimiento_salud=establecimiento)
            )
    
    return queryset


def _verificar_acceso_objeto(user, objeto):
    """
    Verifica si el usuario tiene acceso a un objeto específico
    """
    if not _tiene_acceso_prevencion(user):
        return False
    
    # Administradores pueden acceder a todo
    if user.is_superuser or _es_administrador(user):
        return True
    
    # Verificar acceso por establecimiento
    establecimiento_usuario = _obtener_establecimiento_usuario(user)
    if establecimiento_usuario:
        if isinstance(objeto, PrevencionQuimioprofilaxis):
            if objeto.paciente:
                return objeto.paciente.establecimiento_salud == establecimiento_usuario
            elif objeto.contacto:
                return objeto.contacto.paciente_indice.establecimiento_salud == establecimiento_usuario
        
        elif isinstance(objeto, PrevencionVacunacionBCG):
            return objeto.paciente.establecimiento_salud == establecimiento_usuario
        
        elif isinstance(objeto, PrevencionSeguimiento):
            if objeto.quimioprofilaxis:
                return _verificar_acceso_objeto(user, objeto.quimioprofilaxis)
            elif objeto.vacunacion:
                return _verificar_acceso_objeto(user, objeto.vacunacion)
    
    return False


# =============================================================================
# FUNCIONES DE AYUDA PARA ACCESO A ATRIBUTOS DE USUARIO
# =============================================================================

def _tiene_perfil_usuario(user):
    """Verifica si el usuario tiene perfil de usuario"""
    return hasattr(user, 'usuariosusuario')


def _es_administrador(user):
    """Verifica si el usuario es administrador de forma segura"""
    if _tiene_perfil_usuario(user):
        return getattr(user.usuariosusuario, 'es_administrador', False)
    return False


def _obtener_rol_usuario(user):
    """Obtiene el rol del usuario de forma segura"""
    if _tiene_perfil_usuario(user):
        return getattr(user.usuariosusuario, 'rol', None)
    return None


def _obtener_establecimiento_usuario(user):
    """Obtiene el establecimiento del usuario de forma segura"""
    if _tiene_perfil_usuario(user):
        return getattr(user.usuariosusuario, 'establecimiento', None)
    return None


# =============================================================================
# VISTAS PARA QUIMIOPROFILAXIS
# =============================================================================

class QuimioprofilaxisListView(LoginRequiredMixin, ListView):
    """
    Vista para listar quimioprofilaxis con control de acceso por roles
    """
    model = PrevencionQuimioprofilaxis
    template_name = 'prevencion/quimioprofilaxis_lista.html'
    context_object_name = 'quimioprofilaxis'
    paginate_by = 20

    def get_queryset(self):
        """Filtra las quimioprofilaxis según el rol y establecimiento del usuario"""
        if not _tiene_acceso_prevencion(self.request.user):
            return PrevencionQuimioprofilaxis.objects.none()
        
        queryset = _filtrar_por_establecimiento(
            PrevencionQuimioprofilaxis.objects.all(), 
            self.request.user,
            'quimioprofilaxis'
        )
        
        # Aplicar filtros adicionales
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Búsqueda por nombre o RUT
        busqueda = self.request.GET.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(paciente__nombre__icontains=busqueda) |
                Q(paciente__rut__icontains=busqueda) |
                Q(contacto__nombre_contacto__icontains=busqueda) |
                Q(contacto__rut_contacto__icontains=busqueda)
            )
        
        return queryset.select_related('paciente', 'contacto').order_by('-fecha_registro')

    def get_context_data(self, **kwargs):
        """Agrega información de permisos al contexto"""
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = _tiene_acceso_prevencion(self.request.user)
        context['puede_editar'] = _tiene_acceso_prevencion(self.request.user)
        
        # Verificar si es administrador para mostrar opciones de eliminación
        context['es_administrador'] = (
            self.request.user.is_superuser or 
            _es_administrador(self.request.user)
        )
        
        return context


class QuimioprofilaxisCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear quimioprofilaxis con control de acceso
    """
    model = PrevencionQuimioprofilaxis
    form_class = QuimioprofilaxisForm
    template_name = 'prevencion/quimioprofilaxis_form.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de acceder a la vista"""
        if not _tiene_acceso_prevencion(request.user):
            messages.error(request, 'No tiene permisos para crear quimioprofilaxis.')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pasa el usuario al formulario para filtrado"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Asigna el usuario que registra y muestra mensaje de éxito"""
        form.instance.usuario_registro = self.request.user
        messages.success(self.request, 'Quimioprofilaxis creada correctamente.')
        return super().form_valid(form)


class QuimioprofilaxisUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar quimioprofilaxis con control de acceso
    """
    model = PrevencionQuimioprofilaxis
    form_class = QuimioprofilaxisForm
    template_name = 'prevencion/quimioprofilaxis_form.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de acceder a la vista"""
        self.object = self.get_object()
        
        if not _verificar_acceso_objeto(request.user, self.object):
            messages.error(request, 'No tiene permisos para editar esta quimioprofilaxis.')
            return self.handle_no_permission()
            
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pasa el usuario al formulario para filtrado"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Muestra mensaje de éxito al actualizar"""
        messages.success(self.request, 'Quimioprofilaxis actualizada correctamente.')
        return super().form_valid(form)


class QuimioprofilaxisDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver detalle de quimioprofilaxis con control de acceso
    """
    model = PrevencionQuimioprofilaxis
    template_name = 'prevencion/quimioprofilaxis_detalle.html'

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de acceder a la vista"""
        self.object = self.get_object()
        
        if not _verificar_acceso_objeto(request.user, self.object):
            messages.error(request, 'No tiene permisos para ver esta quimioprofilaxis.')
            return self.handle_no_permission()
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega información de permisos al contexto"""
        context = super().get_context_data(**kwargs)
        context['puede_editar'] = _verificar_acceso_objeto(self.request.user, self.object)
        context['es_administrador'] = (
            self.request.user.is_superuser or 
            _es_administrador(self.request.user)
        )
        return context


class QuimioprofilaxisDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar quimioprofilaxis (solo administradores)
    """
    model = PrevencionQuimioprofilaxis
    template_name = 'prevencion/quimioprofilaxis_confirmar_eliminar.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def dispatch(self, request, *args, **kwargs):
        """Solo administradores pueden eliminar"""
        if not (request.user.is_superuser or _es_administrador(request.user)):
            messages.error(request, 'Solo los administradores pueden eliminar quimioprofilaxis.')
            return self.handle_no_permission()
            
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Muestra mensaje de éxito al eliminar"""
        messages.success(request, 'Quimioprofilaxis eliminada correctamente.')
        return super().delete(request, *args, **kwargs)


# =============================================================================
# VISTAS PARA VACUNACIÓN BCG
# =============================================================================

class VacunacionBCGListView(LoginRequiredMixin, ListView):
    """
    Vista para listar vacunaciones BCG con control de acceso
    """
    model = PrevencionVacunacionBCG
    template_name = 'prevencion/vacunacion_lista.html'
    context_object_name = 'vacunaciones'
    paginate_by = 20

    def get_queryset(self):
        """Filtra las vacunaciones según el rol y establecimiento del usuario"""
        if not _tiene_acceso_prevencion(self.request.user):
            return PrevencionVacunacionBCG.objects.none()
        
        queryset = _filtrar_por_establecimiento(
            PrevencionVacunacionBCG.objects.all(), 
            self.request.user,
            'vacunacion'
        )
        
        # Búsqueda por nombre o RUT del paciente
        busqueda = self.request.GET.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(paciente__nombre__icontains=busqueda) |
                Q(paciente__rut__icontains=busqueda)
            )
        
        return queryset.select_related('paciente').order_by('-fecha_registro')


class VacunacionBCGCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear vacunación BCG con control de acceso
    """
    model = PrevencionVacunacionBCG
    form_class = VacunacionBCGForm
    template_name = 'prevencion/vacunacion_form.html'
    success_url = reverse_lazy('prevencion:vacunacion_lista')

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de acceder a la vista"""
        if not _tiene_acceso_prevencion(request.user):
            messages.error(request, 'No tiene permisos para registrar vacunaciones BCG.')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pasa el usuario al formulario para filtrado"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Asigna el usuario que registra y muestra mensaje de éxito"""
        form.instance.usuario_registro = self.request.user
        messages.success(self.request, 'Vacunación BCG registrada correctamente.')
        return super().form_valid(form)


# =============================================================================
# VISTAS PARA SEGUIMIENTOS
# =============================================================================

class SeguimientoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear seguimientos con control de acceso
    """
    model = PrevencionSeguimiento
    form_class = SeguimientoForm
    template_name = 'prevencion/seguimiento_form.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de acceder a la vista"""
        if not _tiene_acceso_prevencion(request.user):
            messages.error(request, 'No tiene permisos para crear seguimientos.')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pasa el request y usuario al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Asigna el usuario que registra y muestra mensaje de éxito"""
        form.instance.usuario_registro = self.request.user
        messages.success(self.request, 'Seguimiento registrado correctamente.')
        return super().form_valid(form)


# =============================================================================
# VISTAS AJAX PARA BÚSQUEDA
# =============================================================================

@login_required
def buscar_paciente_contacto_ajax(request):
    """
    Vista AJAX para buscar pacientes y contactos por RUT
    """
    rut = request.GET.get('rut', '').strip()
    
    if not rut:
        return JsonResponse({'error': 'RUT requerido'}, status=400)
    
    if not _tiene_acceso_prevencion(request.user):
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    resultados = {
        'pacientes': [],
        'contactos': []
    }
    
    # Buscar pacientes
    pacientes_qs = PacientesPaciente.objects.filter(estado='activo')
    if not (request.user.is_superuser or _es_administrador(request.user)):
        establecimiento = _obtener_establecimiento_usuario(request.user)
        if establecimiento:
            pacientes_qs = pacientes_qs.filter(establecimiento_salud=establecimiento)
    
    pacientes = pacientes_qs.filter(rut__icontains=rut)[:5]
    
    for paciente in pacientes:
        resultados['pacientes'].append({
            'id': paciente.id,
            'rut': paciente.rut,
            'nombre': paciente.nombre,
            'tipo': 'paciente',
            'edad': paciente.get_edad(),
            'establecimiento': paciente.establecimiento_salud
        })
    
    # Buscar contactos
    contactos_qs = ContactosContacto.objects.all()
    if not (request.user.is_superuser or _es_administrador(request.user)):
        establecimiento = _obtener_establecimiento_usuario(request.user)
        if establecimiento:
            contactos_qs = contactos_qs.filter(
                paciente_indice__establecimiento_salud=establecimiento
            )
    
    contactos = contactos_qs.filter(rut_contacto__icontains=rut)[:5]
    
    for contacto in contactos:
        resultados['contactos'].append({
            'id': contacto.id,
            'rut': contacto.rut_contacto,
            'nombre': contacto.nombre_contacto,
            'tipo': 'contacto',
            'parentesco': contacto.get_parentesco_display(),
            'paciente_indice': str(contacto.paciente_indice)
        })
    
    return JsonResponse(resultados)