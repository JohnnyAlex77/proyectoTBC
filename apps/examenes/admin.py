# apps/examenes/admin.py
from django.contrib import admin
from .models import ExamenesExamenbacteriologico

@admin.register(ExamenesExamenbacteriologico)
class ExamenBacteriologicoAdmin(admin.ModelAdmin):
    list_display = [
        'paciente', 'tipo_examen', 'tipo_muestra', 'fecha_toma_muestra', 
        'resultado', 'sensibilidad', 'usuario_registro'
    ]
    list_filter = [
        'tipo_examen', 'tipo_muestra', 'resultado', 'sensibilidad',
        'fecha_toma_muestra', 'fecha_resultado'
    ]
    search_fields = [
        'paciente__nombre', 'paciente__apellido', 'paciente__run',
        'observaciones'
    ]
    readonly_fields = ['usuario_registro', 'fecha_registro', 'fecha_actualizacion']
    date_hierarchy = 'fecha_toma_muestra'
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('paciente',)
        }),
        ('Detalles del Examen', {
            'fields': (
                'tipo_examen', 'tipo_muestra', 'fecha_toma_muestra',
                'fecha_ingreso_laboratorio', 'fecha_resultado'
            )
        }),
        ('Resultados', {
            'fields': (
                'resultado', 'resultado_cuantitativo', 'sensibilidad', 'observaciones'
            )
        }),
        ('Metadatos', {
            'fields': ('usuario_registro', 'fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.usuario_registro_id:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)