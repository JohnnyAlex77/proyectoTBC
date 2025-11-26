# apps/examenes/apps.py
from django.apps import AppConfig

class ExamenesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.examenes'
    verbose_name = 'Exámenes Bacteriológicos'
    
    def ready(self):
        try:
            import apps.examenes.signals
        except ImportError:
            pass