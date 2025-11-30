# apps/tratamientos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, timedelta
from .models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from .forms import TratamientoForm, EsquemaMedicamentoForm, DosisAdministradaForm, TratamientoUpdateForm
from apps.pacientes.models import PacientesPaciente as Paciente

# Funciones auxiliares para control de acceso
def _tiene_acceso_tratamiento(user, tratamiento):
    """
    Verifica si el usuario tiene acceso al tratamiento específico
    """
    # Administradores tienen acceso completo
    if user.has_perm('tratamientos.view_all_tratamientos') or user.is_superuser:
        return True
        
    # Verificar si el usuario tiene perfil y establecimiento
    if hasattr(user, 'perfilusuario'):
        establecimiento_usuario = user.perfilusuario.establecimiento
        establecimiento_paciente = tratamiento.paciente.establecimiento_salud
        return establecimiento_usuario == establecimiento_paciente
        
    return False

def _tiene_acceso_paciente(user, paciente):
    """
    Verifica si el usuario tiene acceso al paciente específico
    """
    # Administradores tienen acceso completo
    if user.has_perm('pacientes.view_all_pacientes') or user.is_superuser:
        return True
        
    # Verificar si el usuario tiene perfil y establecimiento
    if hasattr(user, 'perfilusuario'):
        establecimiento_usuario = user.perfilusuario.establecimiento
        return establecimiento_usuario == paciente.establecimiento_salud
        
    return False

def _filtrar_por_establecimiento(queryset, user):
    """
    Filtra el queryset por establecimiento si el usuario no es administrador
    """
    if not user.has_perm('tratamientos.view_all_tratamientos') and hasattr(user, 'perfilusuario'):
        establecimiento = user.perfilusuario.establecimiento
        return queryset.filter(paciente__establecimiento_salud=establecimiento)
    return queryset

# Vistas principales con control de roles
@login_required
@permission_required('tratamientos.view_tratamiento', raise_exception=True)
def lista_tratamientos(request):
    """
    Lista tratamientos con control de acceso por roles
    Filtra según los permisos del usuario y establecimiento
    """
    # Obtener tratamientos base
    tratamientos = Tratamiento.objects.all().select_related('paciente', 'usuario_registro')
    
    # Aplicar filtro por establecimiento si no es administrador
    tratamientos = _filtrar_por_establecimiento(tratamientos, request.user)

    # Aplicar filtros adicionales
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

    # Obtener pacientes activos filtrados por establecimiento
    pacientes_activos = Paciente.objects.filter(
        estado__in=['activo', 'Activo', 'Activo en tratamiento']
    )
    pacientes_activos = _filtrar_por_establecimiento(pacientes_activos, request.user).order_by('nombre')

    # Estadísticas filtradas
    total_tratamientos = tratamientos.count()
    tratamientos_activos = tratamientos.filter(
        Q(resultado_final__isnull=True) | Q(resultado_final='En Tratamiento')
    ).count()
    tratamientos_completados = tratamientos.filter(
        resultado_final__in=['Curación', 'Tratamiento Completo']
    ).count()
    
    # Dosis pendientes filtradas
    fecha_hoy = date.today()
    fecha_limite = fecha_hoy + timedelta(days=7)
    dosis_pendientes = DosisAdministrada.objects.filter(
        administrada=False,
        fecha_dosis__range=[fecha_hoy, fecha_limite]
    )
    dosis_pendientes = _filtrar_por_establecimiento(
        dosis_pendientes.select_related('esquema_medicamento__tratamiento__paciente'), 
        request.user
    )
    dosis_pendientes_count = dosis_pendientes.count()

    context = {
        'tratamientos': tratamientos,
        'total_tratamientos': total_tratamientos,
        'tratamientos_activos': tratamientos_activos,
        'tratamientos_completados': tratamientos_completados,
        'dosis_pendientes_count': dosis_pendientes_count,
        'pacientes': pacientes_activos,
        'puede_crear': request.user.has_perm('tratamientos.add_tratamiento'),
        'puede_editar': request.user.has_perm('tratamientos.change_tratamiento'),
        'puede_eliminar': request.user.has_perm('tratamientos.delete_tratamiento'),
    }
    return render(request, 'tratamientos/lista_tratamientos.html', context)

@login_required
@permission_required('tratamientos.view_tratamiento', raise_exception=True)
def detalle_tratamiento(request, pk):
    """
    Muestra detalle de tratamiento con control de acceso
    """
    tratamiento = get_object_or_404(
        Tratamiento.objects.select_related('paciente', 'usuario_registro'),
        pk=pk
    )
    
    # Verificar acceso al tratamiento específico
    if not _tiene_acceso_tratamiento(request.user, tratamiento):
        messages.error(request, 'No tiene permisos para acceder a este tratamiento.')
        return redirect('tratamientos:lista')
    
    esquemas_medicamento = EsquemaMedicamento.objects.filter(tratamiento=tratamiento)

    context = {
        'tratamiento': tratamiento,
        'esquemas_medicamento': esquemas_medicamento,
        'puede_editar': request.user.has_perm('tratamientos.change_tratamiento'),
        'puede_eliminar': request.user.has_perm('tratamientos.delete_tratamiento'),
        'puede_agregar_medicamento': request.user.has_perm('tratamientos.add_esquemamedicamento'),
        'puede_registrar_dosis': request.user.has_perm('tratamientos.add_dosisadministrada'),
    }
    return render(request, 'tratamientos/detalle_tratamiento.html', context)

@login_required
@permission_required('tratamientos.add_tratamiento', raise_exception=True)
def crear_tratamiento(request):
    """
    Crear nuevo tratamiento con validación de tratamiento activo
    """
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    tratamiento = form.save(commit=False)
                    tratamiento.usuario_registro = request.user
                    
                    # Verificar acceso al paciente seleccionado
                    if not _tiene_acceso_paciente(request.user, tratamiento.paciente):
                        messages.error(request, 'No tiene permisos para crear tratamientos para este paciente.')
                        return render(request, 'tratamientos/tratamiento_form.html', {'form': form, 'titulo': 'Crear Nuevo Tratamiento'})
                    
                    # VERIFICACIÓN FINAL - Asegurar que no existe tratamiento activo
                    tratamiento_activo_existente = Tratamiento.objects.filter(
                        paciente=tratamiento.paciente,
                        resultado_final__in=[None, 'En Tratamiento']
                    ).exists()
                    
                    if tratamiento_activo_existente:
                        messages.error(request, f'El paciente {tratamiento.paciente.nombre} ya tiene un tratamiento activo. No se puede crear otro tratamiento.')
                        return render(request, 'tratamientos/tratamiento_form.html', {'form': form, 'titulo': 'Crear Nuevo Tratamiento'})
                    
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
@permission_required('tratamientos.change_tratamiento', raise_exception=True)
def editar_tratamiento(request, pk):
    """
    Editar tratamiento existente con control de acceso
    """
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    
    # Verificar acceso al tratamiento específico
    if not _tiene_acceso_tratamiento(request.user, tratamiento):
        messages.error(request, 'No tiene permisos para editar este tratamiento.')
        return redirect('tratamientos:lista')

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
@permission_required('tratamientos.delete_tratamiento', raise_exception=True)
def eliminar_tratamiento(request, pk):
    """
    Eliminar tratamiento con control de acceso
    """
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    
    # Verificar acceso al tratamiento específico
    if not _tiene_acceso_tratamiento(request.user, tratamiento):
        messages.error(request, 'No tiene permisos para eliminar este tratamiento.')
        return redirect('tratamientos:lista')

    if request.method == 'POST':
        nombre_paciente = tratamiento.paciente.nombre
        tratamiento.delete()
        messages.success(request, f'Tratamiento de {nombre_paciente} eliminado exitosamente.')
        return redirect('tratamientos:lista')

    context = {
        'tratamiento': tratamiento
    }
    return render(request, 'tratamientos/confirmar_eliminar.html', context)

@login_required
@permission_required('tratamientos.add_esquemamedicamento', raise_exception=True)
def crear_esquema_medicamento(request, tratamiento_pk):
    """
    Agregar medicamento al esquema de tratamiento con control de acceso
    """
    tratamiento = get_object_or_404(Tratamiento, pk=tratamiento_pk)
    
    # Verificar acceso al tratamiento
    if not _tiene_acceso_tratamiento(request.user, tratamiento):
        messages.error(request, 'No tiene permisos para agregar medicamentos a este tratamiento.')
        return redirect('tratamientos:lista')

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
@permission_required('tratamientos.delete_esquemamedicamento', raise_exception=True)
def eliminar_esquema_medicamento(request, pk):
    """
    Eliminar medicamento del esquema con control de acceso
    """
    esquema = get_object_or_404(EsquemaMedicamento, pk=pk)
    tratamiento_pk = esquema.tratamiento.pk
    
    # Verificar acceso al tratamiento
    if not _tiene_acceso_tratamiento(request.user, esquema.tratamiento):
        messages.error(request, 'No tiene permisos para eliminar medicamentos de este tratamiento.')
        return redirect('tratamientos:lista')

    if request.method == 'POST':
        esquema.delete()
        messages.success(request, 'Esquema de medicamento eliminado exitosamente.')
        return redirect('tratamientos:detalle', pk=tratamiento_pk)

    context = {
        'esquema': esquema
    }
    return render(request, 'tratamientos/confirmar_eliminar_medicamento.html', context)

@login_required
@permission_required('tratamientos.add_dosisadministrada', raise_exception=True)
def registrar_dosis(request, esquema_pk):
    """
    Registrar administración de dosis con control de acceso
    """
    esquema = get_object_or_404(EsquemaMedicamento, pk=esquema_pk)
    
    # Verificar acceso al tratamiento
    if not _tiene_acceso_tratamiento(request.user, esquema.tratamiento):
        messages.error(request, 'No tiene permisos para registrar dosis en este tratamiento.')
        return redirect('tratamientos:lista')

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
@permission_required('tratamientos.view_dosisadministrada', raise_exception=True)
def lista_dosis_pendientes(request):
    """
    Lista dosis pendientes de administración con control de acceso
    """
    fecha_hoy = date.today()
    fecha_limite = fecha_hoy + timedelta(days=7)

    dosis_pendientes = DosisAdministrada.objects.filter(
        administrada=False,
        fecha_dosis__range=[fecha_hoy, fecha_limite]
    ).select_related(
        'esquema_medicamento__tratamiento__paciente',
        'usuario_administracion'
    ).order_by('fecha_dosis')

    # Filtrar por establecimiento si no es administrador
    dosis_pendientes = _filtrar_por_establecimiento(dosis_pendientes, request.user)

    context = {
        'dosis_pendientes': dosis_pendientes,
        'fecha_hoy': fecha_hoy,
        'fecha_limite': fecha_limite,
    }
    return render(request, 'tratamientos/lista_dosis_pendientes.html', context)

@login_required
@permission_required('tratamientos.view_dosisadministrada', raise_exception=True)
def control_dosis(request):
    """
    Control de dosis con estadísticas filtradas por establecimiento
    """
    fecha_hoy = date.today()
    
    # Obtener dosis del día filtradas por establecimiento
    dosis_base = DosisAdministrada.objects.filter(fecha_dosis=fecha_hoy)
    dosis_base = _filtrar_por_establecimiento(dosis_base, request.user)
    
    dosis_hoy = dosis_base.count()
    dosis_administradas_hoy = dosis_base.filter(administrada=True).count()
    dosis_pendientes_hoy = dosis_base.filter(administrada=False).count()

    context = {
        'dosis_hoy': dosis_hoy,
        'dosis_administradas_hoy': dosis_administradas_hoy,
        'dosis_pendientes_hoy': dosis_pendientes_hoy,
        'fecha_hoy': fecha_hoy,
    }
    return render(request, 'tratamientos/control_dosis.html', context)

@login_required
@permission_required('tratamientos.view_dosisadministrada', raise_exception=True)
def calendario_dosis(request):
    """
    Calendario de dosis filtrado por establecimiento
    """
    hoy = date.today()
    mes_actual = hoy.month
    año_actual = hoy.year
    
    dosis_mes = DosisAdministrada.objects.filter(
        fecha_dosis__month=mes_actual,
        fecha_dosis__year=año_actual
    ).select_related(
        'esquema_medicamento__tratamiento__paciente'
    ).order_by('fecha_dosis')

    # Filtrar por establecimiento
    dosis_mes = _filtrar_por_establecimiento(dosis_mes, request.user)

    context = {
        'dosis_mes': dosis_mes,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'hoy': hoy,
    }
    return render(request, 'tratamientos/calendario_dosis.html', context)

# Vistas AJAX
@login_required
def buscar_paciente_por_rut(request):
    """
    Vista AJAX para buscar pacientes por RUT con control de acceso
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut = request.GET.get('rut', '').strip()
        
        if not rut:
            return JsonResponse({'error': 'Debe ingresar un RUT'}, status=400)
        
        try:
            # Limpiar el RUT
            rut_limpio = rut.replace('.', '').replace('-', '').upper()
            
            # Buscar paciente por RUT de diferentes formas
            paciente = None
            
            # Búsquedas múltiples
            paciente = Paciente.objects.filter(rut__iexact=rut).first()
            if not paciente:
                paciente = Paciente.objects.filter(rut__iexact=rut_limpio).first()
            if not paciente:
                todos_pacientes = Paciente.objects.all()
                for p in todos_pacientes:
                    rut_paciente_limpio = p.rut.replace('.', '').replace('-', '').upper()
                    if rut_limpio == rut_paciente_limpio:
                        paciente = p
                        break
            if not paciente:
                solo_numeros = ''.join(filter(str.isdigit, rut_limpio))
                if solo_numeros:
                    todos_pacientes = Paciente.objects.all()
                    for p in todos_pacientes:
                        rut_paciente_numeros = ''.join(filter(str.isdigit, p.rut))
                        if solo_numeros == rut_paciente_numeros:
                            paciente = p
                            break
            
            if paciente:
                # Verificar acceso al paciente encontrado
                if not _tiene_acceso_paciente(request.user, paciente):
                    return JsonResponse({
                        'encontrado': False,
                        'error': 'No tiene permisos para acceder a este paciente.'
                    }, status=403)
                
                # Verificar si el paciente ya tiene tratamiento activo
                tratamiento_activo = Tratamiento.objects.filter(
                    paciente=paciente,
                    resultado_final__in=[None, 'En Tratamiento']
                ).first()
                
                # Obtener información del tratamiento activo si existe
                tratamiento_info = None
                if tratamiento_activo:
                    esquema_display = tratamiento_activo.get_esquema_display()
                    tratamiento_info = {
                        'id': tratamiento_activo.id,
                        'esquema': esquema_display,
                        'fecha_inicio': tratamiento_activo.fecha_inicio.strftime('%d/%m/%Y'),
                        'fecha_termino_estimada': tratamiento_activo.fecha_termino_estimada.strftime('%d/%m/%Y'),
                        'usuario_registro': tratamiento_activo.usuario_registro.get_full_name(),
                        'dias_transcurridos': (date.today() - tratamiento_activo.fecha_inicio).days
                    }
                
                # Obtener listas de enfermedades y alergias
                enfermedades_list = paciente.get_enfermedades_list()
                alergias_list = paciente.get_alergias_list()
                
                # Función auxiliar para obtener display de choices
                def get_display_value(value, choices):
                    for choice_value, choice_label in choices:
                        if choice_value == value:
                            return choice_label
                    return value
                
                # Preparar respuesta
                respuesta = {
                    'encontrado': True,
                    'paciente': {
                        'id': paciente.id,
                        'nombre': paciente.nombre,
                        'rut': paciente.rut,
                        'edad': paciente.get_edad(),
                        'establecimiento_salud': paciente.establecimiento_salud,
                        'fecha_nacimiento': paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'No registrada',
                        'sexo': get_display_value(paciente.sexo, Paciente.SEXO_CHOICES),
                        'tipo_tbc': get_display_value(paciente.tipo_tbc, Paciente.TIPO_TBC_CHOICES),
                        'enfermedades_preexistentes': enfermedades_list,
                        'alergias': alergias_list,
                        'tiene_enfermedades': len(enfermedades_list) > 0,
                        'tiene_alergias': len(alergias_list) > 0,
                        'domicilio': paciente.domicilio,
                        'comuna': paciente.comuna,
                        'telefono': paciente.telefono,
                        'fecha_diagnostico': paciente.fecha_diagnostico.strftime('%d/%m/%Y') if paciente.fecha_diagnostico else 'No registrada',
                        'estado': get_display_value(paciente.estado, Paciente.ESTADO_CHOICES),
                    },
                    'tratamiento_activo': tratamiento_activo is not None,
                    'tratamiento_info': tratamiento_info
                }
                
                return JsonResponse(respuesta)
            else:
                return JsonResponse({
                    'encontrado': False,
                    'error': f'No se encontró ningún paciente con el RUT: {rut}'
                }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'encontrado': False,
                'error': f'Error en la búsqueda: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def verificar_paciente_tratamiento_activo(request, paciente_id):
    """
    Verifica si un paciente tiene tratamiento activo (AJAX)
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            
            # Verificar acceso al paciente
            if not _tiene_acceso_paciente(request.user, paciente):
                return JsonResponse({
                    'error': 'No tiene permisos para acceder a este paciente.'
                }, status=403)
            
            tratamiento_activo = Tratamiento.objects.filter(
                paciente=paciente,
                resultado_final__in=[None, 'En Tratamiento']
            ).exists()
            
            tratamiento_info = None
            if tratamiento_activo:
                tratamiento = Tratamiento.objects.filter(
                    paciente=paciente,
                    resultado_final__in=[None, 'En Tratamiento']
                ).first()
                if tratamiento:
                    esquema_display = tratamiento.get_esquema_display()
                    tratamiento_info = {
                        'id': tratamiento.id,
                        'esquema': esquema_display,
                        'fecha_inicio': tratamiento.fecha_inicio.strftime('%d/%m/%Y'),
                        'usuario_registro': tratamiento.usuario_registro.get_full_name()
                    }
            
            return JsonResponse({
                'tiene_tratamiento_activo': tratamiento_activo,
                'tratamiento_info': tratamiento_info
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Error al verificar tratamiento: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista temporal para debug
@login_required
def debug_pacientes(request):
    """
    Vista temporal para debug de pacientes (solo administradores)
    """
    if not request.user.is_superuser and not request.user.has_perm('tratamientos.view_all_tratamientos'):
        return JsonResponse({'error': 'No tiene permisos para acceder a esta vista.'}, status=403)
        
    pacientes = Paciente.objects.all().values('id', 'rut', 'nombre')
    return JsonResponse({'pacientes': list(pacientes)})