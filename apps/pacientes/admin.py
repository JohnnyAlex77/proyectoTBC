from django.contrib import admin
from .models import PacientesPaciente

@admin.register(PacientesPaciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'fecha_diagnostico', 'estado', 'usuario_registro')
    search_fields = ('rut', 'nombre', 'comuna')
    list_filter = ('estado', 'sexo', 'tipo_tbc', 'comuna')
    readonly_fields = ('fecha_registro', 'usuario_registro')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Si es un nuevo objeto
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)