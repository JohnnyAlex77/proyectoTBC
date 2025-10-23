from django.contrib import admin
from .models import PacientesPaciente

@admin.register(PacientesPaciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('rut','nombre','fecha_diagnostico','estado','usuario_registro')
    search_fields = ('rut','nombre','comuna')
