# apps/contactos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import ContactosContacto
from .forms import ContactoForm
from apps.pacientes.models import PacientesPaciente

def _tiene_acceso_contacto(user, contacto):
    """Verifica si el usuario tiene acceso al contacto específico"""
    if user.has_perm('contactos.view_all_contactos') or user.is_superuser:
        return True
        
    if hasattr(user, 'perfilusuario'):
        establecimiento_usuario = user.perfilusuario.establecimiento
        establecimiento_paciente = contacto.paciente_indice.establecimiento_salud
        return establecimiento_usuario == establecimiento_paciente
        
    return False

def _filtrar_por_establecimiento(queryset, user):
    """Filtra el queryset por establecimiento si el usuario no es administrador"""
    if not user.has_perm('contactos.view_all_contactos') and hasattr(user, 'perfilusuario'):
        establecimiento = user.perfilusuario.establecimiento
        return queryset.filter(paciente_indice__establecimiento_salud=establecimiento)
    return queryset

@login_required
def lista_contactos(request):
    """Lista contactos con control de acceso por establecimiento"""
    contactos = ContactosContacto.objects.all().select_related('paciente_indice').order_by('-fecha_registro')
    contactos = _filtrar_por_establecimiento(contactos, request.user)
    return render(request, 'contactos/listar_contactos.html', {'contactos': contactos})

@login_required
def crear_contacto(request):
    """Crear nuevo contacto con control de acceso y buscador de pacientes"""
    if request.method == 'POST':
        form = ContactoForm(request.POST, user=request.user)  # Pasar user al formulario
        if form.is_valid():
            contacto = form.save()
            messages.success(request, 'Contacto registrado correctamente.')
            return redirect('contactos:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ContactoForm(user=request.user)  # Pasar user al formulario
    return render(request, 'contactos/contacto_form.html', {'form': form, 'contacto': None})

@login_required
def editar_contacto(request, pk):
    """Editar contacto existente con control de acceso"""
    contacto = get_object_or_404(ContactosContacto, pk=pk)
    
    # Verificar acceso al contacto
    if not _tiene_acceso_contacto(request.user, contacto):
        messages.error(request, 'No tienes permisos para editar este contacto.')
        return redirect('contactos:lista')
    
    if request.method == 'POST':
        form = ContactoForm(request.POST, instance=contacto, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contacto actualizado correctamente.')
            return redirect('contactos:detalle', pk=contacto.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ContactoForm(instance=contacto, user=request.user)
    
    # Pasar el contacto al contexto para que el template pueda acceder a los datos
    return render(request, 'contactos/contacto_form.html', {
        'form': form, 
        'contacto': contacto  # Esto es importante para que el template muestre los datos actuales
    })

@login_required
def detalle_contacto(request, pk):
    """Ver detalle del contacto con control de acceso"""
    contacto = get_object_or_404(ContactosContacto, pk=pk)
    
    # Verificar acceso al contacto
    if not _tiene_acceso_contacto(request.user, contacto):
        messages.error(request, 'No tienes permisos para ver este contacto.')
        return redirect('contactos:lista')
    
    return render(request, 'contactos/detalle_contacto.html', {'contacto': contacto})

@login_required
def eliminar_contacto(request, pk):
    """Eliminar contacto con control de acceso"""
    contacto = get_object_or_404(ContactosContacto, pk=pk)
    
    # Verificar acceso al contacto
    if not _tiene_acceso_contacto(request.user, contacto):
        messages.error(request, 'No tienes permisos para eliminar este contacto.')
        return redirect('contactos:lista')

    if request.method == 'POST':
        nombre_contacto = contacto.nombre_contacto
        contacto.delete()
        messages.success(request, f'Contacto "{nombre_contacto}" eliminado correctamente.')
        return redirect('contactos:lista')

    return render(request, 'contactos/confirmar_eliminar.html', {'contacto': contacto})

@login_required
def buscar_contactos(request):
    """Buscar contactos con control de acceso por establecimiento"""
    query = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', '')
    tipo_filtro = request.GET.get('tipo', '')

    contactos = ContactosContacto.objects.all().select_related('paciente_indice')
    contactos = _filtrar_por_establecimiento(contactos, request.user)

    if query:
        contactos = contactos.filter(
            Q(nombre_contacto__icontains=query) |
            Q(rut_contacto__icontains=query) |
            Q(paciente_indice__nombre__icontains=query)
        )

    if estado_filtro:
        contactos = contactos.filter(estado_estudio=estado_filtro)

    if tipo_filtro:
        contactos = contactos.filter(tipo_contacto=tipo_filtro)

    contactos = contactos.order_by('-fecha_registro')

    return render(request, 'contactos/buscar_contacto.html', {
        'contactos': contactos,
        'query': query,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro
    })

@login_required
def buscar_pacientes_ajax(request):
    """Búsqueda AJAX de pacientes para el formulario de contactos"""
    query = request.GET.get('q', '')
    
    if query:
        # Filtrar pacientes según acceso del usuario
        pacientes = PacientesPaciente.objects.all()
        if not request.user.has_perm('contactos.view_all_contactos') and hasattr(request.user, 'perfilusuario'):
            establecimiento = request.user.perfilusuario.establecimiento
            pacientes = pacientes.filter(establecimiento_salud=establecimiento)
        
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | Q(rut__icontains=query)
        )[:10]  # Limitar resultados para mejor performance
        
        resultados = []
        for paciente in pacientes:
            resultados.append({
                'id': paciente.id,
                'text': f"{paciente.nombre} - {paciente.rut} - {paciente.establecimiento_salud}"
            })
        
        return JsonResponse({'results': resultados})
    
    return JsonResponse({'results': []})