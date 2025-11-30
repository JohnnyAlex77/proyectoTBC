# apps/examenes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

from .models import ExamenesExamenbacteriologico
from .forms import ExamenBacteriologicoForm
from apps.pacientes.models import PacientesPaciente
from apps.laboratorio.models import LaboratorioRedLaboratorios

# Funciones auxiliares para control de acceso
def _tiene_acceso_examen(user, examen):
    """Verifica si el usuario tiene acceso al examen específico"""
    if user.has_perm('examenes.view_all_examenes') or user.is_superuser:
        return True
        
    if hasattr(user, 'usuariosusuario'):
        establecimiento_usuario = user.usuariosusuario.establecimiento
        # Verificar si el paciente tiene establecimiento_salud
        establecimiento_paciente = examen.paciente.establecimiento_salud
        return establecimiento_usuario == establecimiento_paciente
        
    return False

def _filtrar_por_establecimiento(queryset, user):
    """Filtra el queryset por establecimiento si el usuario no es administrador"""
    if not user.has_perm('examenes.view_all_examenes') and hasattr(user, 'usuariosusuario'):
        establecimiento = user.usuariosusuario.establecimiento
        return queryset.filter(paciente__establecimiento_salud=establecimiento)
    return queryset

def _puede_crear_examen(user):
    """Verifica si el usuario puede crear exámenes"""
    return user.has_perm('examenes.add_examenesexamenbacteriologico') or user.is_superuser

def _puede_editar_examen(user):
    """Verifica si el usuario puede editar exámenes"""
    return user.has_perm('examenes.change_examenesexamenbacteriologico') or user.is_superuser

def _puede_eliminar_examen(user):
    """Verifica si el usuario puede eliminar exámenes"""
    return user.has_perm('examenes.delete_examenesexamenbacteriologico') or user.is_superuser

@login_required
def lista_examenes(request):
    """Lista todos los exámenes bacteriológicos con control de acceso"""
    query = request.GET.get('q', '')
    tipo_examen = request.GET.get('tipo_examen', '')
    resultado = request.GET.get('resultado', '')

    # Obtener queryset base con control de acceso
    examenes = ExamenesExamenbacteriologico.objects.select_related('paciente', 'usuario_registro')
    examenes = _filtrar_por_establecimiento(examenes, request.user)

    # Aplicar filtros
    if query:
        examenes = examenes.filter(
            Q(paciente__nombre__icontains=query) |
            Q(paciente__rut__icontains=query) |
            Q(observaciones_muestra__icontains=query) |
            Q(observaciones_resultado__icontains=query)
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
        'puede_crear': _puede_crear_examen(request.user),
        'puede_editar': _puede_editar_examen(request.user),
        'puede_eliminar': _puede_eliminar_examen(request.user),
    }
    return render(request, 'examenes/lista_examenes.html', context)

@login_required
def detalle_examen(request, examen_id):
    """Detalle de un examen bacteriológico con control de acceso"""
    examen = get_object_or_404(
        ExamenesExamenbacteriologico.objects.select_related('paciente', 'usuario_registro'),
        pk=examen_id
    )
    
    # Verificar acceso al examen
    if not _tiene_acceso_examen(request.user, examen):
        messages.error(request, 'No tiene permisos para acceder a este examen.')
        return redirect('examenes:lista_examenes')

    context = {
        'examen': examen,
        'puede_editar': _puede_editar_examen(request.user),
        'puede_eliminar': _puede_eliminar_examen(request.user),
    }
    return render(request, 'examenes/detalle_examen.html', context)

@login_required
def crear_examen(request):
    """Crear nuevo examen bacteriológico con control de acceso"""
    if not _puede_crear_examen(request.user):
        messages.error(request, 'No tiene permisos para crear exámenes.')
        return redirect('examenes:lista_examenes')

    if request.method == 'POST':
        form = ExamenBacteriologicoForm(request.POST, user=request.user)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.usuario_registro = request.user
            examen.save()
            messages.success(request, 'Examen bacteriológico creado exitosamente.')
            return redirect('examenes:detalle_examen', examen_id=examen.pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ExamenBacteriologicoForm(user=request.user)

    context = {
        'form': form,
        'titulo': 'Nuevo Examen Bacteriológico',
    }
    return render(request, 'examenes/crear_editar_examen.html', context)

@login_required
def editar_examen(request, examen_id):
    """Editar examen bacteriológico existente con control de acceso"""
    if not _puede_editar_examen(request.user):
        messages.error(request, 'No tiene permisos para editar exámenes.')
        return redirect('examenes:lista_examenes')

    examen = get_object_or_404(ExamenesExamenbacteriologico, pk=examen_id)
    
    # Verificar acceso al examen
    if not _tiene_acceso_examen(request.user, examen):
        messages.error(request, 'No tiene permisos para editar este examen.')
        return redirect('examenes:lista_examenes')

    if request.method == 'POST':
        form = ExamenBacteriologicoForm(request.POST, instance=examen, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Examen bacteriológico actualizado exitosamente.')
            return redirect('examenes:detalle_examen', examen_id=examen.pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ExamenBacteriologicoForm(instance=examen, user=request.user)

    context = {
        'form': form,
        'titulo': 'Editar Examen Bacteriológico',
        'examen': examen,
    }
    return render(request, 'examenes/crear_editar_examen.html', context)

@login_required
def eliminar_examen(request, examen_id):
    """Eliminar examen bacteriológico con control de acceso"""
    if not _puede_eliminar_examen(request.user):
        messages.error(request, 'No tiene permisos para eliminar exámenes.')
        return redirect('examenes:lista_examenes')

    examen = get_object_or_404(ExamenesExamenbacteriologico, pk=examen_id)
    
    # Verificar acceso al examen
    if not _tiene_acceso_examen(request.user, examen):
        messages.error(request, 'No tiene permisos para eliminar este examen.')
        return redirect('examenes:lista_examenes')

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
    """Lista todos los exámenes de un paciente específico con control de acceso"""
    from apps.pacientes.models import PacientesPaciente

    paciente = get_object_or_404(PacientesPaciente, pk=paciente_id)
    
    # Verificar acceso al paciente
    if not _tiene_acceso_examen(request.user, paciente):
        messages.error(request, 'No tiene permisos para acceder a los exámenes de este paciente.')
        return redirect('examenes:lista_examenes')

    examenes = ExamenesExamenbacteriologico.objects.filter(paciente=paciente)
    examenes = _filtrar_por_establecimiento(examenes, request.user)
    examenes = examenes.order_by('-fecha_toma_muestra')

    context = {
        'paciente': paciente,
        'examenes': examenes,
        'puede_crear': _puede_crear_examen(request.user),
    }
    return render(request, 'examenes/examenes_por_paciente.html', context)

# Vistas AJAX para búsquedas
@login_required
def buscar_paciente_por_rut(request):
    """Buscar paciente por RUT - API para AJAX"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut = request.GET.get('rut', '').strip()
        
        if rut:
            try:
                # Buscar paciente por RUT usando el campo correcto
                paciente = PacientesPaciente.objects.get(rut=rut)
                
                # Verificar acceso al paciente
                if not _tiene_acceso_examen(request.user, paciente):
                    return JsonResponse({
                        'encontrado': False,
                        'error': 'No tiene acceso a este paciente.'
                    })
                
                # Obtener datos del paciente según el modelo real
                datos_paciente = {
                    'encontrado': True,
                    'id': paciente.pk,
                    'nombre': paciente.nombre,
                    'rut': paciente.rut,
                    'edad': paciente.get_edad(),
                    'sexo': paciente.get_sexo_display(),
                }
                
                return JsonResponse(datos_paciente)
            except PacientesPaciente.DoesNotExist:
                return JsonResponse({
                    'encontrado': False,
                    'error': 'Paciente no encontrado.'
                })
            except Exception as e:
                return JsonResponse({
                    'encontrado': False,
                    'error': f'Error en la búsqueda: {str(e)}'
                })
        
        return JsonResponse({
            'encontrado': False,
            'error': 'RUT no proporcionado.'
        })
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@login_required
def buscar_laboratorio_por_nombre(request):
    """Buscar laboratorio por nombre - API para AJAX"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nombre = request.GET.get('nombre', '').strip()
        
        if nombre:
            try:
                # Buscar laboratorios por nombre
                laboratorios = LaboratorioRedLaboratorios.objects.filter(
                    nombre__icontains=nombre,
                    activo=True
                )[:10]  # Limitar resultados
                
                resultados = []
                for lab in laboratorios:
                    lab_data = {
                        'id': lab.pk,
                        'nombre': lab.nombre,
                        'tipo': lab.get_tipo_display(),
                    }
                    
                    # Agregar campos opcionales si existen
                    if hasattr(lab, 'direccion'):
                        lab_data['direccion'] = lab.direccion
                    
                    resultados.append(lab_data)
                
                return JsonResponse({
                    'encontrados': len(resultados) > 0,
                    'resultados': resultados
                })
            except Exception as e:
                return JsonResponse({
                    'encontrados': False,
                    'error': f'Error en la búsqueda: {str(e)}'
                })
        
        return JsonResponse({
            'encontrados': False,
            'error': 'Nombre no proporcionado.'
        })
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)