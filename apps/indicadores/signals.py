# apps/indicadores/signals.py - VERSIÓN CORREGIDA
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

@receiver(post_save, sender='pacientes.PacientesPaciente')
def actualizar_indicadores_paciente(sender, instance, created, **kwargs):
    """Actualiza indicadores cuando cambia un paciente - VERSIÓN SEGURA"""
    try:
        # Verificar cambios importantes en el paciente
        if 'estado' in kwargs.get('update_fields', []) or created:
            from .services import CalculadorIndicadores
            from .models import Establecimiento
            
            # Solo procesar si el paciente tiene fecha de diagnóstico
            if instance.fecha_diagnostico:
                año = instance.fecha_diagnostico.year
                trimestre = 'Q' + str((instance.fecha_diagnostico.month - 1) // 3 + 1)
                
                # Usar el primer establecimiento disponible
                establecimiento = Establecimiento.objects.first()
                if establecimiento:
                    # Ejecutar en background para no bloquear la respuesta
                    import threading
                    
                    def calcular_en_background():
                        try:
                            CalculadorIndicadores.calcular_indicadores_cohorte(
                                año, trimestre, establecimiento
                            )
                        except Exception as e:
                            # Solo loggear el error, no interrumpir
                            print(f"Error en cálculo de indicadores en background: {e}")
                    
                    # Ejecutar en un hilo separado
                    thread = threading.Thread(target=calcular_en_background)
                    thread.daemon = True
                    thread.start()
                    
    except Exception as e:
        # Silenciar errores para no interrumpir el flujo principal
        print(f"Error en señal de indicadores (manejo general): {e}")

@receiver(post_save, sender='tratamientos.Tratamiento')
def actualizar_indicadores_tratamiento(sender, instance, **kwargs):
    """Actualiza indicadores cuando cambia un tratamiento - VERSIÓN SEGURA"""
    try:
        from .services import CalculadorIndicadores
        from .models import Establecimiento
        
        if instance.paciente and instance.fecha_inicio:
            año = instance.fecha_inicio.year
            trimestre = 'Q' + str((instance.fecha_inicio.month - 1) // 3 + 1)
            
            # Usar el primer establecimiento disponible
            establecimiento = Establecimiento.objects.first()
            if establecimiento:
                # Ejecutar en background
                import threading
                
                def calcular_en_background():
                    try:
                        CalculadorIndicadores.calcular_indicadores_cohorte(
                            año, trimestre, establecimiento
                        )
                    except Exception as e:
                        print(f"Error en cálculo de indicadores (tratamiento) en background: {e}")
                
                thread = threading.Thread(target=calcular_en_background)
                thread.daemon = True
                thread.start()
                
    except Exception as e:
        print(f"Error en señal de indicadores (tratamiento): {e}")