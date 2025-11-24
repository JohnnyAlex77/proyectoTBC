# signals.py - Señales para integración automática
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.pacientes.models import PacientesPaciente
from apps.tratamientos.models import Tratamiento
from apps.contactos.models import ContactosContacto
from .services import CalculadorIndicadores
from django.utils import timezone

@receiver(post_save, sender=PacientesPaciente)
def actualizar_indicadores_paciente(sender, instance, created, **kwargs):
    """Actualiza indicadores cuando cambia un paciente"""
    if created or instance.estado_changed:
        # Recalcular indicadores del trimestre actual
        año = instance.fecha_diagnostico.year if instance.fecha_diagnostico else timezone.now().year
        trimestre = 'Q' + str((instance.fecha_diagnostico.month - 1) // 3 + 1) if instance.fecha_diagnostico else 'Q1'
        
        # Usar el primer establecimiento disponible
        from .models import Establecimiento
        establecimiento = Establecimiento.objects.first()
        if establecimiento:
            CalculadorIndicadores.calcular_indicadores_cohorte(
                año, trimestre, establecimiento
            )

@receiver(post_save, sender=Tratamiento)
def actualizar_indicadores_tratamiento(sender, instance, **kwargs):
    """Actualiza indicadores cuando cambia un tratamiento"""
    if instance.paciente:
        año = instance.fecha_inicio.year
        trimestre = 'Q' + str((instance.fecha_inicio.month - 1) // 3 + 1)
        
        # Usar el primer establecimiento disponible
        from .models import Establecimiento
        establecimiento = Establecimiento.objects.first()
        if establecimiento:
            CalculadorIndicadores.calcular_indicadores_cohorte(
                año, trimestre, establecimiento
            )