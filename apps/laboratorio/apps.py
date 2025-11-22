from django.apps import AppConfig

class LaboratorioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.laboratorio'
    verbose_name = 'Laboratorio TBC'
    
    def ready(self):
        import apps.laboratorio.signals