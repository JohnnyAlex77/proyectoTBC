# apps/indicadores/urls.py - ACTUALIZADO
from django.urls import path
from . import views

app_name = 'indicadores'

urlpatterns = [
    path('dashboard/', views.DashboardPrincipalView.as_view(), name='dashboard'),
    path('cohorte/', views.IndicadoresCohorteView.as_view(), name='indicadores_cohorte'),
    path('operacionales/', views.IndicadoresOperacionalesView.as_view(), name='indicadores_operacionales'),
    path('prevencion/', views.IndicadoresPrevencionView.as_view(), name='indicadores_prevencion'),
    path('alertas/', views.AlertasView.as_view(), name='alertas_lista'),
    path('reportes/', views.ReportesView.as_view(), name='reportes_gerenciales'),
    
    # Exportación Excel
    path('reportes/cohorte/excel/', views.GenerarReporteCohorteExcelView.as_view(), 
         name='exportar_excel_cohorte'),
    path('reportes/operacional/excel/', views.GenerarReporteOperacionalExcelView.as_view(), 
         name='exportar_excel_operacional'),
    path('reportes/completo/excel/', views.GenerarReporteCompletoExcelView.as_view(), 
         name='exportar_excel_completo'),
    
    # Exportación PDF
    path('reportes/cohorte/pdf/', views.GenerarReporteCohortePDFView.as_view(), 
         name='exportar_pdf_cohorte'),
    path('reportes/operacional/pdf/', views.GenerarReporteOperacionalPDFView.as_view(), 
         name='exportar_pdf_operacional'),
    
    # Otras URLs existentes
    path('actualizar-indicadores/', views.ActualizarIndicadoresView.as_view(), name='actualizar_indicadores'),
    path('alertas/<int:alerta_id>/resolver/', views.ResolverAlertaView.as_view(), name='resolver_alerta'),
    path('alertas/crear/', views.CrearAlertaView.as_view(), name='crear_alerta'),
    path('alertas/<int:alerta_id>/eliminar/', views.EliminarAlertaView.as_view(), name='eliminar_alerta'),
]