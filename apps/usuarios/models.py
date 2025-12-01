from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UsuariosUsuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('enfermera', 'Enfermera'),
        ('medico', 'Médico'),
        ('tecnologo', 'Tecnologo Médico'),
        ('paramedico', 'Técnico Paramédico'),
    ]

    # Relación OneToOne con el User de Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='usuariosusuario'
    )

    # Campos adicionales
    rut = models.CharField(max_length=15, unique=True)
    rol = models.CharField(max_length=50, choices=ROL_CHOICES, default='enfermera')
    establecimiento = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.rut})"

    # Propiedades para acceder fácilmente a los datos del User
    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def is_active(self):
        return self.user.is_active

    @property
    def is_staff(self):
        return self.user.is_staff

    @property
    def is_superuser(self):
        return self.user.is_superuser

    # Método para obtener el nombre del rol
    def get_rol_display(self):
        """Devuelve el nombre legible del rol"""
        for codigo, nombre in self.ROL_CHOICES:
            if codigo == self.rol:
                return nombre
        return self.rol

    # Método para verificar permisos por rol
    def tiene_permiso_rol(self, roles_permitidos):
        return self.rol in roles_permitidos or self.user.is_superuser

    # Métodos específicos por rol
    def es_administrador(self):
        return self.rol == 'admin' or self.user.is_superuser

    def es_medico(self):
        return self.rol == 'medico'

    def es_enfermera(self):
        return self.rol == 'enfermera'

    def es_tecnologo(self):
        return self.rol == 'tecnologo'

    def es_paramedico(self):
        return self.rol == 'paramedico'

# Señal para crear perfil automáticamente
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un perfil de usuario automáticamente cuando se crea un User"""
    if created and not hasattr(instance, 'usuariosusuario'):
        # Crear perfil por defecto con todos los campos requeridos
        UsuariosUsuario.objects.create(
            user=instance,
            rut=f"temp-{instance.username}",
            rol='enfermera',
            establecimiento='Sin asignar',
            telefono='' 
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el perfil de usuario cuando se guarda el User"""
    try:
        instance.usuariosusuario.save()
    except UsuariosUsuario.DoesNotExist:
        # Si no existe, crear el perfil
        UsuariosUsuario.objects.create(
            user=instance,
            rut=f"temp-{instance.username}",
            rol='enfermera',
            establecimiento='Sin asignar'
        )