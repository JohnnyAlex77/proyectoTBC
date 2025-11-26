from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import PrevencionQuimioprofilaxis, PrevencionVacunacionBCG, PrevencionSeguimiento
from .forms import QuimioprofilaxisForm, VacunacionBCGForm, SeguimientoForm

class QuimioprofilaxisListView(LoginRequiredMixin, ListView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionQuimioprofilaxis
    template_name = 'prevencion/quimioprofilaxis_lista.html'
    context_object_name = 'quimioprofilaxis'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset.select_related('paciente', 'contacto').order_by('-fecha_registro')

class QuimioprofilaxisCreateView(LoginRequiredMixin, CreateView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionQuimioprofilaxis
    form_class = QuimioprofilaxisForm
    template_name = 'prevencion/quimioprofilaxis_form.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def form_valid(self, form):
        form.instance.usuario_registro = self.request.user
        messages.success(self.request, 'Quimioprofilaxis creada correctamente.')
        return super().form_valid(form)

class QuimioprofilaxisUpdateView(LoginRequiredMixin, UpdateView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionQuimioprofilaxis
    form_class = QuimioprofilaxisForm
    template_name = 'prevencion/quimioprofilaxis_form.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Quimioprofilaxis actualizada correctamente.')
        return super().form_valid(form)

class QuimioprofilaxisDetailView(LoginRequiredMixin, DetailView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionQuimioprofilaxis
    template_name = 'prevencion/quimioprofilaxis_detalle.html'

class QuimioprofilaxisDeleteView(LoginRequiredMixin, DeleteView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionQuimioprofilaxis
    template_name = 'prevencion/quimioprofilaxis_confirmar_eliminar.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Quimioprofilaxis eliminada correctamente.')
        return super().delete(request, *args, **kwargs)

class VacunacionBCGListView(LoginRequiredMixin, ListView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionVacunacionBCG
    template_name = 'prevencion/vacunacion_lista.html'
    context_object_name = 'vacunaciones'
    paginate_by = 20

class VacunacionBCGCreateView(LoginRequiredMixin, CreateView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionVacunacionBCG
    form_class = VacunacionBCGForm
    template_name = 'prevencion/vacunacion_form.html'
    success_url = reverse_lazy('prevencion:vacunacion_lista')

    def form_valid(self, form):
        form.instance.usuario_registro = self.request.user
        messages.success(self.request, 'Vacunación BCG registrada correctamente.')
        return super().form_valid(form)

class SeguimientoCreateView(LoginRequiredMixin, CreateView):  # REMOVED: PermissionRequiredMixin
    model = PrevencionSeguimiento
    form_class = SeguimientoForm
    template_name = 'prevencion/seguimiento_form.html'
    success_url = reverse_lazy('prevencion:quimioprofilaxis_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.usuario_registro = self.request.user
        messages.success(self.request, 'Seguimiento registrado correctamente.')
        return super().form_valid(form)