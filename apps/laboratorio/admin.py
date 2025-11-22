from django.contrib import admin
from .models import LaboratorioRedLaboratorios, LaboratorioControlCalidad, LaboratorioTarjetero, LaboratorioIndicadores

@admin.register(LaboratorioRedLaboratorios)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'comuna', 'responsable', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'comuna']
    list_editable = ['activo']

@admin.register(LaboratorioControlCalidad)
class ControlCalidadAdmin(admin.ModelAdmin):
    list_display = ['laboratorio', 'fecha_control', 'tipo_control', 'resultado', 'usuario_responsable']
    list_filter = ['tipo_control', 'resultado', 'fecha_control']
    search_fields = ['laboratorio__nombre', 'observaciones']
    date_hierarchy = 'fecha_control'

@admin.register(LaboratorioTarjetero)
class TarjeteroAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'fecha_deteccion', 'tipo_muestra', 'resultado', 'laboratorio_referencia']
    list_filter = ['tipo_muestra', 'fecha_deteccion']
    search_fields = ['paciente__nombre', 'resultado']
    raw_id_fields = ['paciente', 'examen']

@admin.register(LaboratorioIndicadores)
class IndicadoresAdmin(admin.ModelAdmin):
    list_display = ['laboratorio', 'periodo', 'muestras_recibidas', 'muestras_procesadas', 'positivos']
    list_filter = ['periodo', 'laboratorio']
    search_fields = ['laboratorio__nombre']