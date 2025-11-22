from django.contrib import admin
from .models import (
    Establecimiento,
    IndicadoresCohorte,
    IndicadoresOperacionales,
    IndicadoresPrevencion,
    Alerta,
    ReportePersonalizado
)

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'tipo', 'region']
    list_filter = ['tipo', 'region']
    search_fields = ['nombre', 'codigo']

@admin.register(IndicadoresCohorte)
class IndicadoresCohorteAdmin(admin.ModelAdmin):
    list_display = [
        'año',
        'trimestre',
        'establecimiento',
        'total_casos',
        'exito_tratamiento_porcentaje',
        'tasa_abandono'
    ]
    list_filter = ['año', 'trimestre', 'establecimiento']
    readonly_fields = ['total_casos', 'exito_tratamiento_porcentaje', 'tasa_abandono', 'tasa_fallecimiento']

@admin.register(IndicadoresOperacionales)
class IndicadoresOperacionalesAdmin(admin.ModelAdmin):
    list_display = [
        'establecimiento',
        'periodo',
        'indice_pesquisa',
        'cobertura_estudio_contactos',
        'adherencia_taes'
    ]
    list_filter = ['establecimiento', 'periodo']
    readonly_fields = ['indice_pesquisa', 'cobertura_estudio_contactos', 'adherencia_taes']

@admin.register(IndicadoresPrevencion)
class IndicadoresPrevencionAdmin(admin.ModelAdmin):
    list_display = [
        'establecimiento',
        'periodo',
        'cobertura_quimioprofilaxis',
        'adherencia_quimioprofilaxis',
        'cobertura_vacunacion_bcg'
    ]
    list_filter = ['establecimiento', 'periodo']
    readonly_fields = [
        'cobertura_quimioprofilaxis',
        'adherencia_quimioprofilaxis',
        'cobertura_vacunacion_bcg'
    ]

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo',
        'tipo',
        'nivel',
        'establecimiento',
        'resuelta',
        'fecha_creacion'
    ]
    list_filter = ['tipo', 'nivel', 'resuelta', 'establecimiento']
    actions = ['marcar_como_resueltas']
    
    def marcar_como_resueltas(self, request, queryset):
        updated = queryset.update(resuelta=True)
        self.message_user(request, f'{updated} alertas marcadas como resueltas.')
    marcar_como_resueltas.short_description = "Marcar alertas seleccionadas como resueltas"

@admin.register(ReportePersonalizado)
class ReportePersonalizadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario_creador', 'compartido', 'fecha_creacion']
    list_filter = ['compartido', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']