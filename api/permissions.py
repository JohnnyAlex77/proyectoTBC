# api/permissions.py
"""
Permisos personalizados para la API del sistema TBC
Control de acceso por rol y establecimiento
"""
from rest_framework import permissions

class EstablecimientoPermission(permissions.BasePermission):
    """
    Permiso para controlar acceso basado en establecimiento del usuario
    """
    def has_permission(self, request, view):
        # Todos los usuarios autenticados tienen acceso básico
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        """
        Verifica si el usuario tiene acceso a un objeto específico
        basado en su establecimiento
        """
        user = request.user
        # Administradores tienen acceso completo
        if user.is_superuser or user.groups.filter(name='Administrador').exists():
            return True
        # Verificar si el usuario tiene perfil con establecimiento
        if hasattr(user, 'perfilusuario'):
            user_establecimiento = user.perfilusuario.establecimiento
            # Verificar si el objeto tiene establecimiento_salud
            if hasattr(obj, 'establecimiento_salud'):
                return user_establecimiento == obj.establecimiento_salud
            # Verificar si el objeto tiene establecimiento relacionado
            if hasattr(obj, 'paciente'):
                return user_establecimiento == obj.paciente.establecimiento_salud
        return False


class IsAdminOrMedico(permissions.BasePermission):
    """
    Permiso solo para administradores y médicos
    """
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        return (user.is_superuser or 
                user.groups.filter(name='Administrador').exists() or
                user.groups.filter(name='Medico').exists())


class IsEnfermeraOrHigher(permissions.BasePermission):
    """
    Permiso para enfermeras y roles superiores
    """
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        grupos_permitidos = ['Administrador', 'Medico', 'Enfermera']
        return (user.is_superuser or 
                user.groups.filter(name__in=grupos_permitidos).exists())


class IsTecnologoOrHigher(permissions.BasePermission):
    """
    Permiso para tecnólogos y roles superiores
    """
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        grupos_permitidos = ['Administrador', 'Medico', 'Enfermera', 'Tecnologo_Medico']
        return (user.is_superuser or 
                user.groups.filter(name__in=grupos_permitidos).exists())