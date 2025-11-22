from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from datetime import date, timedelta
from .models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from .forms import TratamientoForm, EsquemaMedicamentoForm, DosisAdministradaForm, TratamientoUpdateForm
from apps.pacientes.models import PacientesPaciente as Paciente

# VISTAS DE TRATAMIENTOS
@login_required
def lista_tratamientos(request):
    """Lista todos los tratamientos con filtros"""
    tratamientos = Tratamiento.objects.all().select_related('paciente', 'usuario_registro')

    # Filtros
    estado = request.GET.get('estado')
    paciente_id = request.GET.get('paciente')
    esquema = request.GET.get('esquema')

    if estado:
        if estado == 'activos':
            tratamientos = tratamientos.filter(Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento'))
        elif estado == 'completados':
            tratamientos = tratamientos.filter(resultado_final__in=['Curación', 'Tratamiento Completo'])

    if paciente_id:
        tratamientos = tratamientos.filter(paciente_id=paciente_id)

    if esquema:
        tratamientos = tratamientos.filter(esquema=esquema)

    # Obtener TODOS los pacientes activos para el filtro - USANDO LOS ESTADOS CORRECTOS
    pacientes_activos = Paciente.objects.filter(
        estado__in=['activo', 'Activo', 'Activo en tratamiento']
    ).order_by('nombre')

    # Estadísticas REALES
    total_tratamientos = Tratamiento.objects.count()
    tratamientos_activos = Tratamiento.objects.filter(
        Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')
    ).count()
    tratamientos_completados = Tratamiento.objects.filter(
        resultado_final__in=['Curación', 'Tratamiento Completo']
    ).count()
    
    # Calcular dosis pendientes reales
    fecha_hoy = date.today()
    fecha_limite = fecha_hoy + timedelta(days=7)
    dosis_pendientes_count = DosisAdministrada.objects.filter(
        administrada=False,
        fecha_dosis__range=[fecha_hoy, fecha_limite]
    ).count()

    context = {
        'tratamientos': tratamientos,
        'total_tratamientos': total_tratamientos,
        'tratamientos_activos': tratamientos_activos,
        'tratamientos_completados': tratamientos_completados,
        'dosis_pendientes_count': dosis_pendientes_count,
        'pacientes': pacientes_activos,
    }
    return render(request, 'tratamientos/lista_tratamientos.html', context)

@login_required
def detalle_tratamiento(request, pk):
    """Vista detallada de un tratamiento"""
    tratamiento = get_object_or_404(
        Tratamiento.objects.select_related('paciente', 'usuario_registro'),
        pk=pk
    )
    esquemas_medicamento = tratamiento.esquemas_medicamento.all()

    context = {
        'tratamiento': tratamiento,
        'esquemas_medicamento': esquemas_medicamento,
    }
    return render(request, 'tratamientos/detalle_tratamiento.html', context)

@login_required
def crear_tratamiento(request):
    """Crear un nuevo tratamiento"""
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    tratamiento = form.save(commit=False)
                    tratamiento.usuario_registro = request.user
                    tratamiento.save()
                    messages.success(request, 'Tratamiento creado exitosamente.')
                    return redirect('tratamientos:detalle', pk=tratamiento.pk)
            except Exception as e:
                messages.error(request, f'Error al crear tratamiento: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = TratamientoForm()

    context = {
        'form': form,
        'titulo': 'Crear Nuevo Tratamiento'
    }
    return render(request, 'tratamientos/tratamiento_form.html', context)

@login_required
def editar_tratamiento(request, pk):
    """Editar un tratamiento existente"""
    tratamiento = get_object_or_404(Tratamiento, pk=pk)

    if request.method == 'POST':
        form = TratamientoUpdateForm(request.POST, instance=tratamiento)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Tratamiento actualizado exitosamente.')
                return redirect('tratamientos:detalle', pk=tratamiento.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar tratamiento: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = TratamientoUpdateForm(instance=tratamiento)

    context = {
        'form': form,
        'tratamiento': tratamiento,
        'titulo': f'Editar Tratamiento - {tratamiento.paciente.nombre}'
    }
    return render(request, 'tratamientos/tratamiento_form.html', context)

@login_required
def eliminar_tratamiento(request, pk):
    """Eliminar un tratamiento"""
    tratamiento = get_object_or_404(Tratamiento, pk=pk)

    if request.method == 'POST':
        nombre_paciente = tratamiento.paciente.nombre
        tratamiento.delete()
        messages.success(request, f'Tratamiento de {nombre_paciente} eliminado exitosamente.')
        return redirect('tratamientos:lista')

    context = {
        'tratamiento': tratamiento
    }
    return render(request, 'tratamientos/confirmar_eliminar.html', context)

# VISTAS DE ESQUEMAS DE MEDICAMENTOS
@login_required
def crear_esquema_medicamento(request, tratamiento_pk):
    """Crear esquema de medicamento para un tratamiento"""
    tratamiento = get_object_or_404(Tratamiento, pk=tratamiento_pk)

    if request.method == 'POST':
        form = EsquemaMedicamentoForm(request.POST)
        if form.is_valid():
            try:
                esquema = form.save(commit=False)
                esquema.tratamiento = tratamiento
                esquema.save()
                messages.success(request, 'Esquema de medicamento agregado exitosamente.')
                return redirect('tratamientos:detalle', pk=tratamiento.pk)
            except Exception as e:
                messages.error(request, f'Error al crear esquema: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EsquemaMedicamentoForm()

    context = {
        'form': form,
        'tratamiento': tratamiento,
        'titulo': f'Agregar Medicamento - {tratamiento.paciente.nombre}'
    }
    return render(request, 'tratamientos/agregar_medicamento.html', context)

@login_required
def eliminar_esquema_medicamento(request, pk):
    """Eliminar un esquema de medicamento"""
    esquema = get_object_or_404(EsquemaMedicamento, pk=pk)
    tratamiento_pk = esquema.tratamiento.pk

    if request.method == 'POST':
        esquema.delete()
        messages.success(request, 'Esquema de medicamento eliminado exitosamente.')
        return redirect('tratamientos:detalle', pk=tratamiento_pk)

    context = {
        'esquema': esquema
    }
    return render(request, 'tratamientos/confirmar_eliminar_medicamento.html', context)

# VISTAS DE DOSIS ADMINISTRADAS
@login_required
def registrar_dosis(request, esquema_pk):
    """Registrar administración de dosis"""
    esquema = get_object_or_404(EsquemaMedicamento, pk=esquema_pk)

    if request.method == 'POST':
        form = DosisAdministradaForm(request.POST)
        if form.is_valid():
            try:
                dosis = form.save(commit=False)
                dosis.esquema_medicamento = esquema
                dosis.usuario_administracion = request.user
                dosis.save()
                messages.success(request, 'Dosis registrada exitosamente.')
                return redirect('tratamientos:detalle', pk=esquema.tratamiento.pk)
            except Exception as e:
                messages.error(request, f'Error al registrar dosis: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = DosisAdministradaForm()

    context = {
        'form': form,
        'esquema': esquema,
        'titulo': f'Registrar Dosis - {esquema.medicamento}'
    }
    return render(request, 'tratamientos/dosis_form.html', context)

@login_required
def lista_dosis_pendientes(request):
    """Lista de dosis pendientes de administración"""
    fecha_hoy = date.today()
    fecha_limite = fecha_hoy + timedelta(days=7)

    dosis_pendientes = DosisAdministrada.objects.filter(
        administrada=False,
        fecha_dosis__range=[fecha_hoy, fecha_limite]
    ).select_related(
        'esquema_medicamento__tratamiento__paciente',
        'usuario_administracion'
    ).order_by('fecha_dosis')

    context = {
        'dosis_pendientes': dosis_pendientes,
        'fecha_hoy': fecha_hoy,
        'fecha_limite': fecha_limite,
    }
    return render(request, 'tratamientos/lista_dosis_pendientes.html', context)

@login_required
def control_dosis(request):
    """Control general de dosis"""
    context = {}
    return render(request, 'tratamientos/control_dosis.html', context)

@login_required
def calendario_dosis(request):
    """Calendario de administración de dosis"""
    context = {}
    return render(request, 'tratamientos/calendario_dosis.html', context)