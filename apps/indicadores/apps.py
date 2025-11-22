from django.apps import AppConfig

class IndicadoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.indicadores'
    verbose_name = 'Sistema de Indicadores y Analytics'

    def ready(self):
        # Importar señales para integración automática
        try:
            from . import signals
        except ImportError:
            pass