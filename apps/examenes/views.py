# apps/examenes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import ExamenesExamenbacteriologico
from .forms import ExamenBacteriologicoForm

@login_required
def lista_examenes(request):
    """Lista todos los exámenes bacteriológicos"""
    query = request.GET.get('q', '')
    tipo_examen = request.GET.get('tipo_examen', '')
    resultado = request.GET.get('resultado', '')

    examenes = ExamenesExamenbacteriologico.objects.select_related('paciente', 'usuario_registro')

    # Filtros
    if query:
        examenes = examenes.filter(
            Q(paciente__nombre__icontains=query) |
            Q(paciente__apellido__icontains=query) |
            Q(paciente__run__icontains=query) |
            Q(observaciones__icontains=query)
        )
    
    if tipo_examen:
        examenes = examenes.filter(tipo_examen=tipo_examen)

    if resultado:
        examenes = examenes.filter(resultado=resultado)

    examenes = examenes.order_by('-fecha_toma_muestra', '-fecha_registro')

    # Paginación
    paginator = Paginator(examenes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'tipo_examen': tipo_examen,
        'resultado': resultado,
        'TIPO_EXAMEN_CHOICES': ExamenesExamenbacteriologico.TIPO_EXAMEN_CHOICES,
        'RESULTADO_CHOICES': ExamenesExamenbacteriologico.RESULTADO_CHOICES,
    }
    return render(request, 'examenes/lista_examenes.html', context)

@login_required
def detalle_examen(request, examen_id):
    """Detalle de un examen bacteriológico"""
    examen = get_object_or_404(
        ExamenesExamenbacteriologico.objects.select_related('paciente', 'usuario_registro'),
        id=examen_id
    )
    context = {
        'examen': examen,
    }
    return render(request, 'examenes/detalle_examen.html', context)

@login_required
def crear_examen(request):
    """Crear nuevo examen bacteriológico"""
    if request.method == 'POST':
        form = ExamenBacteriologicoForm(request.POST)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.usuario_registro = request.user
            examen.save()
            messages.success(request, 'Examen bacteriológico creado exitosamente.')
            return redirect('examenes:lista_examenes')
    else:
        form = ExamenBacteriologicoForm()

    context = {
        'form': form,
        'titulo': 'Nuevo Examen Bacteriológico',
    }
    return render(request, 'examenes/crear_editar_examen.html', context)

@login_required
def editar_examen(request, examen_id):
    """Editar examen bacteriológico existente"""
    examen = get_object_or_404(ExamenesExamenbacteriologico, id=examen_id)

    if request.method == 'POST':
        form = ExamenBacteriologicoForm(request.POST, instance=examen)
        if form.is_valid():
            form.save()
            messages.success(request, 'Examen bacteriológico actualizado exitosamente.')
            return redirect('examenes:detalle_examen', examen_id=examen.id)
    else:
        form = ExamenBacteriologicoForm(instance=examen)

    context = {
        'form': form,
        'titulo': 'Editar Examen Bacteriológico',
        'examen': examen,
    }
    return render(request, 'examenes/crear_editar_examen.html', context)

@login_required
def eliminar_examen(request, examen_id):
    """Eliminar examen bacteriológico"""
    examen = get_object_or_404(ExamenesExamenbacteriologico, id=examen_id)

    if request.method == 'POST':
        examen.delete()
        messages.success(request, 'Examen bacteriológico eliminado exitosamente.')
        return redirect('examenes:lista_examenes')

    context = {
        'examen': examen,
    }
    return render(request, 'examenes/confirmar_eliminar.html', context)

@login_required
def examenes_por_paciente(request, paciente_id):
    """Lista todos los exámenes de un paciente específico"""
    from apps.pacientes.models import PacientesPaciente

    paciente = get_object_or_404(PacientesPaciente, id=paciente_id)
    examenes = ExamenesExamenbacteriologico.objects.filter(paciente=paciente).order_by('-fecha_toma_muestra')

    context = {
        'paciente': paciente,
        'examenes': examenes,
    }
    return render(request, 'examenes/examenes_por_paciente.html', context)