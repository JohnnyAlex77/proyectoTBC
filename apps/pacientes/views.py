# apps/pacientes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import PacientesPaciente
from .forms import PacienteForm

@login_required
def lista_pacientes(request):
    pacientes = PacientesPaciente.objects.all().order_by('-fecha_registro')
    return render(request, 'pacientes/listar_pacientes.html', {'pacientes': pacientes})

@login_required
def crear_paciente(request):
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
    
    return render(request, 'pacientes/crear_paciente.html', {'form': form})

@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(PacientesPaciente, pk=pk)
    
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
    
    return render(request, 'pacientes/editar_paciente.html', {'form': form, 'paciente': paciente})

@login_required
def detalle_paciente(request, pk):
    paciente = get_object_or_404(PacientesPaciente, pk=pk)
    return render(request, 'pacientes/detalle_paciente.html', {'paciente': paciente})

@login_required
def eliminar_paciente(request, pk):
    paciente = get_object_or_404(PacientesPaciente, pk=pk)
    
    if request.method == 'POST':
        nombre_paciente = paciente.nombre
        paciente.delete()
        messages.success(request, f'Paciente "{nombre_paciente}" eliminado correctamente.')
        return redirect('pacientes:lista')
    
    return render(request, 'pacientes/confirmar_eliminar.html', {'paciente': paciente})

@login_required
def buscar_pacientes(request):
    """Buscar pacientes por diferentes criterios"""
    query = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', '')
    comuna_filtro = request.GET.get('comuna', '')
    
    pacientes = PacientesPaciente.objects.all()
    
    # Búsqueda por texto (nombre, RUT)
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | 
            Q(rut__icontains=query)
        )
    
    # Filtro por estado
    if estado_filtro:
        pacientes = pacientes.filter(estado=estado_filtro)
    
    # Filtro por comuna
    if comuna_filtro:
        pacientes = pacientes.filter(comuna__icontains=comuna_filtro)
    
    pacientes = pacientes.order_by('-fecha_registro')
    
    return render(request, 'pacientes/buscar_pacientes.html', {
        'pacientes': pacientes,
        'query': query,
        'estado_filtro': estado_filtro,
        'comuna_filtro': comuna_filtro
    })