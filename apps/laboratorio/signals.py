from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import LaboratorioControlCalidad, LaboratorioTarjetero

@receiver(post_save, sender=LaboratorioControlCalidad)
def log_control_calidad_creado(sender, instance, created, **kwargs):
    """
    Signal para registrar cuando se crea un control de calidad
    """
    if created:
        print(f"Nuevo control de calidad creado: {instance}")

@receiver(post_save, sender=LaboratorioTarjetero)
def log_tarjetero_creado(sender, instance, created, **kwargs):
    """
    Signal para registrar cuando se crea un registro en el tarjetero
    """
    if created:
        print(f"Nuevo registro en tarjetero: {instance}")

# Puedes agregar más signals según sea necesario