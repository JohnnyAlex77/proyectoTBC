from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash, logout
from django.db import transaction
from .models import UsuariosUsuario
from .forms import UsuarioCreateForm, UsuarioUpdateForm, PasswordChangeCustomForm


# ============================
# DECORADORES DE PERMISOS POR ROL
# ============================

def es_administrador(user):
    """Verifica si el usuario es administrador o superusuario"""
    try:
        if user.is_authenticated:
            usuario_ext = UsuariosUsuario.objects.get(user=user)
            return usuario_ext.rol == 'admin' or user.is_superuser
    except UsuariosUsuario.DoesNotExist:
        pass
    return user.is_authenticated and user.is_superuser


def puede_ver_pacientes(user):
    """Verifica si el usuario puede ver pacientes (todos los roles médicos)"""
    if not user.is_authenticated:
        return False
    try:
        usuario_ext = UsuariosUsuario.objects.get(user=user)
        roles_permitidos = ['admin', 'medico', 'enfermera', 'tecnologo', 'paramedico']
        return usuario_ext.rol in roles_permitidos or user.is_superuser
    except UsuariosUsuario.DoesNotExist:
        return user.is_superuser


def puede_crear_pacientes(user):
    """Verifica si el usuario puede crear pacientes"""
    if not user.is_authenticated:
        return False
    try:
        usuario_ext = UsuariosUsuario.objects.get(user=user)
        roles_permitidos = ['admin', 'medico', 'enfermera']
        return usuario_ext.rol in roles_permitidos or user.is_superuser
    except UsuariosUsuario.DoesNotExist:
        return user.is_superuser


# ===========================================================
# VISTAS PRINCIPALES Y AUTENTICACIÓN
# ===========================================================

@login_required
def dashboard(request):
    """Dashboard personalizado según el rol del usuario"""
    try:
        usuario_ext = UsuariosUsuario.objects.get(user=request.user)

        # Contexto común para todos los dashboards
        context = {
            'usuario': usuario_ext,
        }

        if usuario_ext.rol == 'admin' or request.user.is_superuser:
            # Dashboard de administrador
            from django.contrib.auth.models import User
            from apps.pacientes.models import PacientesPaciente as Paciente

            context_admin = {
                'usuario': usuario_ext,
                'total_usuarios': User.objects.count(),
                'total_pacientes': Paciente.objects.count() if 'apps.pacientes.models' in globals() else 0,
                'total_tratamientos': 0,
                'contactos_pendientes': 0,
            }
            return render(request, 'usuarios/dashboard_admin.html', context_admin)

        elif usuario_ext.rol == 'medico':
            # Dashboard de médico
            context_medico = {
                'usuario': usuario_ext,
                'pacientes_asignados': 25,
                'tratamientos_activos': 15,
                'controles_pendientes': 3,
                'examenes_pendientes': 5,
            }
            return render(request, 'usuarios/dashboard_medico.html', context_medico)

        elif usuario_ext.rol == 'enfermera':
            # Dashboard de enfermera
            context_enfermera = {
                'usuario': usuario_ext,
                'pacientes_cuidado': 15,
                'dosis_hoy': 8,
                'controles_pendientes': 3,
                'visitas_hoy': 5,
            }
            return render(request, 'usuarios/dashboard_enfermera.html', context_enfermera)

        elif usuario_ext.rol == 'tecnologo':
            # Dashboard de tecnólogo
            context_tecnologo = {
                'usuario': usuario_ext,
                'examenes_pendientes': 12,
                'examenes_hoy': 8,
                'resultados_listos': 15,
                'casos_positivos': 2,
            }
            return render(request, 'usuarios/dashboard_tecnologo.html', context_tecnologo)

        elif usuario_ext.rol == 'paramedico':
            # Dashboard de paramédico
            context_paramedico = {
                'usuario': usuario_ext,
                'pacientes_asignados': 18,
                'dosis_hoy': 22,
                'visitas_hoy': 6,
                'seguimientos': 4,
            }
            return render(request, 'usuarios/dashboard_paramedico.html', context_paramedico)

        else:
            # Rol no reconocido - dashboard básico
            return render(request, 'usuarios/dashboard_base.html', {'usuario': usuario_ext})

    except UsuariosUsuario.DoesNotExist:
        # Usuario sin perfil extendido - dashboard básico
        messages.warning(request, 'Por favor complete su perfil de usuario.')
        return render(request, 'usuarios/dashboard_base.html', {'usuario': None})


@login_required
def custom_logout(request):
    """Vista personalizada para logout con template"""
    if request.method == 'POST':
        # Limpiar mensajes existentes antes del logout
        storage = messages.get_messages(request)
        for message in storage:
            pass  # Limpiar todos los mensajes
        
        logout(request)
        request.session.flush()  # Limpia sesión completamente
        
        # Crear nuevo mensaje que solo se mostrará en la página de login
        response = redirect('home')
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return response

    # Si es GET, mostrar página de confirmación
    return render(request, 'usuarios/logout_confirm.html')


# ===========================================================
# VISTAS DE GESTIÓN DE USUARIOS (SOLO ADMINISTRADORES)
# ===========================================================

@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def lista_usuarios(request):
    """Lista todos los usuarios del sistema (solo administradores)"""
    usuarios = UsuariosUsuario.objects.all().select_related('user').order_by('user__first_name')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def crear_usuario(request):
    """Crea un nuevo usuario en el sistema (solo administradores)"""
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    usuario = form.save(commit=False)
                    usuario.save()
                    messages.success(request, f'Usuario {usuario.user.get_full_name()} creado correctamente.')
                    return redirect('usuarios:lista')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = UsuarioCreateForm()
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def editar_usuario(request, pk):
    """Edita un usuario existente (solo administradores)"""
    usuario = get_object_or_404(UsuariosUsuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, f'Usuario {usuario.user.get_full_name()} actualizado correctamente.')
                    return redirect('usuarios:lista')
            except Exception as e:
                messages.error(request, f'Error al actualizar el usuario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        initial_data = {
            'username': usuario.user.username,
            'rut': usuario.rut,
            'email': usuario.user.email,
            'first_name': usuario.user.first_name,
            'last_name': usuario.user.last_name,
            'rol': usuario.rol,
            'establecimiento': usuario.establecimiento,
            'telefono': usuario.telefono
        }
        form = UsuarioUpdateForm(instance=usuario, initial=initial_data)
    
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@user_passes_test(es_administrador, login_url='/usuarios/login/')
def eliminar_usuario(request, pk):
    """Elimina un usuario del sistema (solo administradores)"""
    usuario = get_object_or_404(UsuariosUsuario, pk=pk)

    if request.method == 'POST':
        nombre_usuario = usuario.user.get_full_name()
        try:
            with transaction.atomic():
                usuario.user.delete()
                messages.success(request, f'Usuario {nombre_usuario} eliminado correctamente.')
                return redirect('usuarios:lista')
        except Exception as e:
            messages.error(request, f'Error al eliminar el usuario: {str(e)}')
    return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})


# ===========================================================
# VISTAS DE PERFIL Y CONFIGURACIÓN
# ===========================================================

@login_required
def perfil_usuario(request, pk):
    """Muestra el perfil de un usuario (propio perfil o administradores)"""
    usuario = get_object_or_404(UsuariosUsuario, pk=pk)

    # Solo permitir ver el propio perfil o si es administrador
    if request.user != usuario.user and not es_administrador(request.user):
        messages.error(request, 'No tienes permisos para ver este perfil.')
        return redirect('usuarios:dashboard')

    return render(request, 'usuarios/perfil.html', {'usuario': usuario})


@login_required
def cambiar_password(request):
    """Permite al usuario cambiar su contraseña"""
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Su contraseña fue cambiada exitosamente.')
            return redirect('usuarios:perfil', pk=request.user.usuariosusuario.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PasswordChangeCustomForm(request.user)
    return render(request, 'usuarios/cambiar_password.html', {'form': form})


# ===========================================================
# FUNCIONES AUXILIARES
# ===========================================================

def get_user_dashboard_data(user):
    """Función auxiliar para obtener datos del dashboard según el rol"""
    try:
        usuario_ext = UsuariosUsuario.objects.get(user=user)
        
        if usuario_ext.rol == 'admin' or user.is_superuser:
            from django.contrib.auth.models import User
            from apps.pacientes.models import PacientesPaciente as Paciente
            
            return {
                'total_usuarios': User.objects.count(),
                'total_pacientes': Paciente.objects.count() if 'apps.pacientes.models' in globals() else 0,
                'total_tratamientos': 0,
                'contactos_pendientes': 0,
            }
        elif usuario_ext.rol == 'medico':
            return {
                'pacientes_asignados': 25,
                'tratamientos_activos': 15,
                'controles_pendientes': 3,
                'examenes_pendientes': 5,
            }
        elif usuario_ext.rol == 'enfermera':
            return {
                'pacientes_cuidado': 15,
                'dosis_hoy': 8,
                'controles_pendientes': 3,
                'visitas_hoy': 5,
            }
        elif usuario_ext.rol == 'tecnologo':
            return {
                'examenes_pendientes': 12,
                'examenes_hoy': 8,
                'resultados_listos': 15,
                'casos_positivos': 2,
            }
        elif usuario_ext.rol == 'paramedico':
            return {
                'pacientes_asignados': 18,
                'dosis_hoy': 22,
                'visitas_hoy': 6,
                'seguimientos': 4,
            }
    except UsuariosUsuario.DoesNotExist:
        pass
    
    return {}


def check_user_permissions(user, required_roles):
    """Verifica si el usuario tiene los roles requeridos"""
    try:
        usuario_ext = UsuariosUsuario.objects.get(user=user)
        return usuario_ext.rol in required_roles or user.is_superuser
    except UsuariosUsuario.DoesNotExist:
        return user.is_superuser


# Decorador para verificar permisos de módulo
def require_roles(roles_requeridos):
    """Decorador para verificar que el usuario tenga uno de los roles requeridos"""
    def decorator(view_func):
        @user_passes_test(lambda user: check_user_permissions(user, roles_requeridos) or user.is_superuser)
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator