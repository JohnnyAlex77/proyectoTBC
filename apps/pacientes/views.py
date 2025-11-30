from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .models import PacientesPaciente
from .forms import PacienteForm

@login_required
@permission_required('pacientes.view_pacientespaciente', raise_exception=True)
def lista_pacientes(request):
    """
    Lista todos los pacientes con control de acceso por permisos
    Filtra según los permisos del usuario
    """
    if request.user.has_perm('pacientes.view_pacientespaciente'):
        pacientes = PacientesPaciente.objects.all().order_by('-fecha_registro')
    else:
        pacientes = PacientesPaciente.objects.filter(
            usuario_registro=request.user
        ).order_by('-fecha_registro')
    
    context = {
        'pacientes': pacientes,
        'puede_crear': request.user.has_perm('pacientes.add_pacientespaciente'),
        'puede_editar': request.user.has_perm('pacientes.change_pacientespaciente'),
        'puede_eliminar': request.user.has_perm('pacientes.delete_pacientespaciente'),
    }
    return render(request, 'pacientes/listar_pacientes.html', context)

@login_required
@permission_required('pacientes.add_pacientespaciente', raise_exception=True)
def crear_paciente(request):
    """
    Crear nuevo paciente con control de permisos
    Valida formulario y asigna usuario registrador
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.usuario_registro = request.user
            paciente.save()
            messages.success(request, 'Paciente registrado correctamente.')
            return redirect('pacientes:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PacienteForm()
    
    return render(request, 'pacientes/crear_paciente.html', {
        'form': form,
        'paciente': None
    })

@login_required
@permission_required('pacientes.change_pacientespaciente', raise_exception=True)
def editar_paciente(request, pk):
    """
    Editar paciente existente con control de permisos
    Valida que el usuario tenga permisos de edición
    """
    paciente = get_object_or_404(PacientesPaciente, pk=pk)
    
    if not request.user.has_perm('pacientes.change_pacientespaciente'):
        messages.error(request, 'No tienes permisos para editar pacientes.')
        return redirect('pacientes:lista')
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado correctamente.')
            return redirect('pacientes:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'pacientes/editar_paciente.html', {
        'form': form, 
        'paciente': paciente
    })

@login_required
@permission_required('pacientes.view_pacientespaciente', raise_exception=True)
def detalle_paciente(request, pk):
    """
    Ver detalle de paciente con control de permisos
    Muestra información completa del paciente
    """
    paciente = get_object_or_404(PacientesPaciente, pk=pk)
    
    context = {
        'paciente': paciente,
        'puede_editar': request.user.has_perm('pacientes.change_pacientespaciente'),
        'puede_eliminar': request.user.has_perm('pacientes.delete_pacientespaciente'),
    }
    return render(request, 'pacientes/detalle_paciente.html', context)

@login_required
@permission_required('pacientes.delete_pacientespaciente', raise_exception=True)
def eliminar_paciente(request, pk):
    """
    Eliminar paciente con control de permisos
    Confirma eliminación antes de proceder
    """
    paciente = get_object_or_404(PacientesPaciente, pk=pk)
    
    if request.method == 'POST':
        nombre_paciente = paciente.nombre
        paciente.delete()
        messages.success(request, f'Paciente "{nombre_paciente}" eliminado correctamente.')
        return redirect('pacientes:lista')
    
    context = {
        'paciente': paciente,
        'puede_eliminar': request.user.has_perm('pacientes.delete_pacientespaciente'),
    }
    return render(request, 'pacientes/confirmar_eliminar.html', context)

@login_required
@permission_required('pacientes.view_pacientespaciente', raise_exception=True)
def buscar_pacientes(request):
    """
    Buscar pacientes con control de permisos
    Filtra por nombre, RUT, estado y comuna
    """
    query = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', '')
    comuna_filtro = request.GET.get('comuna', '')

    if request.user.has_perm('pacientes.view_pacientespaciente'):
        pacientes = PacientesPaciente.objects.all()
    else:
        pacientes = PacientesPaciente.objects.filter(usuario_registro=request.user)

    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) |
            Q(rut__icontains=query)
        )

    if estado_filtro:
        pacientes = pacientes.filter(estado=estado_filtro)

    if comuna_filtro:
        pacientes = pacientes.filter(comuna__icontains=comuna_filtro)

    pacientes = pacientes.order_by('-fecha_registro')

    context = {
        'pacientes': pacientes,
        'query': query,
        'estado_filtro': estado_filtro,
        'comuna_filtro': comuna_filtro,
        'puede_editar': request.user.has_perm('pacientes.change_pacientespaciente'),
    }
    return render(request, 'pacientes/buscar_pacientes.html', context)