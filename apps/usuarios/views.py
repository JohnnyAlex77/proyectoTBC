# apps/usuarios/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import UsuariosUsuario
from .forms import UsuarioCreateForm, UsuarioUpdateForm

# Función para verificar si el usuario es administrador
def es_administrador(user):
    try:
        usuario_ext = UsuariosUsuario.objects.get(user__username=user.username)
        return user.is_authenticated and (user.is_superuser or usuario_ext.rol == 'admin')
    except UsuariosUsuario.DoesNotExist:
        return user.is_authenticated and user.is_superuser

# Listado de usuarios
@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def lista_usuarios(request):
    usuarios = UsuariosUsuario.objects.all().order_by('user__first_name')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

# Crear usuario
@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.user.get_full_name()} creado correctamente.')
            return redirect('usuarios:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = UsuarioCreateForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

# Editar usuario
@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def editar_usuario(request, pk):
    usuario = get_object_or_404(UsuariosUsuario, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.user.get_full_name()} actualizado correctamente.')
            return redirect('usuarios:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

# Eliminar usuario
@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(UsuariosUsuario, pk=pk)
    
    if request.method == 'POST':
        nombre_usuario = usuario.user.get_full_name()
        usuario.user.delete()  # Esto elimina también la relación UsuariosUsuario
        messages.success(request, f'Usuario {nombre_usuario} eliminado correctamente.')
        return redirect('usuarios:lista')
    
    return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})

# Ver perfil de usuario
@login_required
def perfil_usuario(request, pk):
    usuario = get_object_or_404(UsuariosUsuario, pk=pk)
    
    # Solo permitir ver el propio perfil o si es administrador
    if request.user != usuario.user and not es_administrador(request.user):
        messages.error(request, 'No tienes permisos para ver este perfil.')
        return redirect('pacientes:lista')
    
    return render(request, 'usuarios/perfil.html', {'usuario': usuario})
