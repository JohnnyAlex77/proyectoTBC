from django.contrib import admin
from .models import PrevencionQuimioprofilaxis, PrevencionVacunacionBCG, PrevencionSeguimiento

@admin.register(PrevencionQuimioprofilaxis)
class QuimioprofilaxisAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_paciente_nombre', 'medicamento', 'fecha_inicio', 'estado', 'adherencia_porcentaje']
    list_filter = ['estado', 'medicamento', 'fecha_inicio']
    search_fields = ['paciente__nombre', 'contacto__nombre']
    date_hierarchy = 'fecha_inicio'

    def get_paciente_nombre(self, obj):
        return obj.paciente.nombre if obj.paciente else obj.contacto.nombre
    get_paciente_nombre.short_description = 'Paciente/Contacto'

@admin.register(PrevencionVacunacionBCG)
class VacunacionBCGAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'fecha_vacunacion', 'lote', 'reaccion', 'usuario_registro']
    list_filter = ['reaccion', 'fecha_vacunacion']
    search_fields = ['paciente__nombre']
    date_hierarchy = 'fecha_vacunacion'

@admin.register(PrevencionSeguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ['tipo_seguimiento', 'fecha_seguimiento', 'usuario_registro']
    list_filter = ['tipo_seguimiento', 'fecha_seguimiento']
    date_hierarchy = 'fecha_seguimiento'