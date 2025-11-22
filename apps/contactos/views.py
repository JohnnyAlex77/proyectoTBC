from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ContactosContacto
from .forms import ContactoForm

@login_required
def lista_contactos(request):
    """Lista todos los contactos"""
    contactos = ContactosContacto.objects.all().select_related('paciente_indice').order_by('-fecha_registro')
    return render(request, 'contactos/listar_contactos.html', {'contactos': contactos})

@login_required
def crear_contacto(request):
    """Crear nuevo contacto"""
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            contacto = form.save()
            messages.success(request, 'Contacto registrado correctamente.')
            return redirect('contactos:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ContactoForm()
    return render(request, 'contactos/contacto_form.html', {'form': form, 'contacto': None})

@login_required
def editar_contacto(request, pk):
    """Editar contacto existente"""
    contacto = get_object_or_404(ContactosContacto, pk=pk)
    if request.method == 'POST':
        form = ContactoForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contacto actualizado correctamente.')
            return redirect('contactos:detalle', pk=contacto.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ContactoForm(instance=contacto)
    return render(request, 'contactos/contacto_form.html', {'form': form, 'contacto': contacto})

@login_required
def detalle_contacto(request, pk):
    """Ver detalle del contacto"""
    contacto = get_object_or_404(ContactosContacto, pk=pk)
    return render(request, 'contactos/detalle_contacto.html', {'contacto': contacto})

@login_required
def eliminar_contacto(request, pk):
    """Eliminar contacto"""
    contacto = get_object_or_404(ContactosContacto, pk=pk)

    if request.method == 'POST':
        nombre_contacto = contacto.nombre_contacto
        contacto.delete()
        messages.success(request, f'Contacto "{nombre_contacto}" eliminado correctamente.')
        return redirect('contactos:lista')

    return render(request, 'contactos/confirmar_eliminar.html', {'contacto': contacto})

@login_required
def buscar_contactos(request):
    """Buscar contactos por diferentes criterios"""
    query = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', '')
    tipo_filtro = request.GET.get('tipo', '')

    contactos = ContactosContacto.objects.all().select_related('paciente_indice')

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