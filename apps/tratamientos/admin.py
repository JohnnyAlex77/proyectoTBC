from django.contrib import admin
from .models import Tratamiento, EsquemaMedicamento, DosisAdministrada

class EsquemaMedicamentoInline(admin.TabularInline):
    model = EsquemaMedicamento
    extra = 1
    fields = ['medicamento', 'dosis_mg', 'frecuencia', 'fase', 'duracion_semanas']

class DosisAdministradaInline(admin.TabularInline):
    model = DosisAdministrada
    extra = 0
    fields = ['fecha_dosis', 'administrada', 'hora_administracion', 'usuario_administracion']
    readonly_fields = ['usuario_administracion']

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'esquema', 'fecha_inicio', 'fecha_termino_estimada', 'esta_activo']
    list_filter = ['esquema', 'fecha_inicio', 'resultado_final']
    search_fields = ['paciente__nombre', 'paciente__rut']
    readonly_fields = ['usuario_registro', 'fecha_registro']
    inlines = [EsquemaMedicamentoInline]
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('paciente', 'usuario_registro')
        }),
        ('Detalles del Tratamiento', {
            'fields': ('esquema', 'fecha_inicio', 'fecha_termino_estimada', 'fecha_termino_real', 'peso_kg')
        }),
        ('Resultados', {
            'fields': ('resultado_final', 'observaciones')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)

@admin.register(EsquemaMedicamento)
class EsquemaMedicamentoAdmin(admin.ModelAdmin):
    list_display = ['medicamento', 'dosis_mg', 'frecuencia', 'fase', 'tratamiento', 'duracion_semanas']
    list_filter = ['medicamento', 'fase', 'frecuencia']
    search_fields = ['tratamiento__paciente__nombre', 'medicamento']

@admin.register(DosisAdministrada)
class DosisAdministradaAdmin(admin.ModelAdmin):
    list_display = ['esquema_medicamento', 'fecha_dosis', 'administrada', 'usuario_administracion']
    list_filter = ['administrada', 'fecha_dosis', 'usuario_administracion']
    readonly_fields = ['usuario_administracion']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario_administracion = request.user
        super().save_model(request, obj, form, change)