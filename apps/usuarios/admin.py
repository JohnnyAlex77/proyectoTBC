from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UsuariosUsuario

# Admin Inline para mostrar los campos adicionales en el User admin
class UsuariosUsuarioInline(admin.StackedInline):
    model = UsuariosUsuario
    can_delete = False
    verbose_name_plural = 'Información adicional'
    fields = ('rut', 'rol', 'establecimiento', 'telefono')  
    extra = 0

# Extender el UserAdmin por defecto
class CustomUserAdmin(UserAdmin):
    inlines = (UsuariosUsuarioInline,)
    list_display = ('username', 'email', 'get_rut', 'first_name', 'last_name', 'is_staff', 'get_rol')
    list_select_related = ('usuariosusuario',)

    def get_rut(self, obj):
        try:
            return obj.usuariosusuario.rut
        except UsuariosUsuario.DoesNotExist:
            return "No asignado"
    get_rut.short_description = 'RUT'

    def get_rol(self, obj):
        try:
            return obj.usuariosusuario.get_rol_display()
        except UsuariosUsuario.DoesNotExist:
            return "No asignado"
    get_rol.short_description = 'Rol'

# Re-registrar el User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Admin para UsuariosUsuario
@admin.register(UsuariosUsuario)
class UsuariosUsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'get_username', 'get_email', 'get_full_name', 'rol', 'establecimiento', 'telefono')
    list_filter = ('rol', 'establecimiento')
    search_fields = ('rut', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('user__first_name', 'user__last_name')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Usuario'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Nombre completo'

    # Form para crear/editar
    def get_form(self, request, obj=None, **kwargs):
        # Si estamos creando un nuevo objeto, hacer que el campo user sea requerido
        if obj is None:
            self.fields = ['user', 'rut', 'rol', 'establecimiento', 'telefono']
        else:
            self.fields = ['rut', 'rol', 'establecimiento', 'telefono']
        return super().get_form(request, obj, **kwargs)

    # Campos para mostrar en el formulario
    fieldsets = (
        (None, {
            'fields': ('user', 'rut', 'rol', 'establecimiento', 'telefono')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Si estamos editando un objeto existente, hacer el campo user de solo lectura
        if obj:
            return ['user']
        return []