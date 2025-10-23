# apps/usuarios/models.py
from django.db import models
from django.contrib.auth.models import User  # Importar User por defecto

class UsuariosUsuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('enfermera', 'Enfermera'),
        ('medico', 'Médico'),
        ('tecnologo', 'Tecnólogo Médico'),
        ('paramedico', 'Técnico Paramédico'),
    ]
    
    # Relación OneToOne con el User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    # Campos adicionales
    rut = models.CharField(unique=True, max_length=12)
    rol = models.CharField(max_length=50, choices=ROL_CHOICES, default='enfermera')
    establecimiento = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        managed = False
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