from django.urls import path
from . import views

app_name = 'laboratorio'

urlpatterns = [
    # Red de Laboratorios
    path('laboratorios/', views.LaboratorioListView.as_view(), name='laboratorios_lista'),
    path('laboratorios/crear/', views.LaboratorioCreateView.as_view(), name='laboratorio_crear'),
    path('laboratorios/<int:pk>/editar/', views.LaboratorioUpdateView.as_view(), name='laboratorio_editar'),
    path('laboratorios/<int:pk>/eliminar/', views.LaboratorioDeleteView.as_view(), name='laboratorio_eliminar'),
    path('laboratorios/<int:pk>/', views.LaboratorioDetailView.as_view(), name='laboratorio_detalle'),

    # Control de Calidad
    path('control-calidad/', views.ControlCalidadListView.as_view(), name='control_calidad_lista'),
    path('control-calidad/crear/', views.ControlCalidadCreateView.as_view(), name='control_calidad_crear'),
    path('control-calidad/<int:pk>/editar/', views.ControlCalidadUpdateView.as_view(), name='control_calidad_editar'),
    path('control-calidad/<int:pk>/eliminar/', views.ControlCalidadDeleteView.as_view(), name='control_calidad_eliminar'),
    path('control-calidad/<int:pk>/', views.ControlCalidadDetailView.as_view(), name='control_calidad_detalle'),

    # Tarjetero de Positivos
    path('tarjetero/', views.TarjeteroListView.as_view(), name='tarjetero_lista'),
    path('tarjetero/crear/', views.TarjeteroCreateView.as_view(), name='tarjetero_crear'),
    path('tarjetero/<int:pk>/editar/', views.TarjeteroUpdateView.as_view(), name='tarjetero_editar'),
    path('tarjetero/<int:pk>/eliminar/', views.TarjeteroDeleteView.as_view(), name='tarjetero_eliminar'),
    path('tarjetero/<int:pk>/', views.TarjeteroDetailView.as_view(), name='tarjetero_detalle'),

    # Indicadores de Laboratorio
    path('indicadores/', views.IndicadoresListView.as_view(), name='indicadores_lista'),
    path('indicadores/crear/', views.IndicadoresCreateView.as_view(), name='indicadores_crear'),
    path('indicadores/<int:pk>/editar/', views.IndicadoresUpdateView.as_view(), name='indicadores_editar'),
    path('indicadores/<int:pk>/eliminar/', views.IndicadoresDeleteView.as_view(), name='indicadores_eliminar'),

    # Dashboard y Reportes
    path('dashboard/', views.DashboardLaboratorioView.as_view(), name='dashboard'),
    path('reportes/', views.ReportesLaboratorioView.as_view(), name='reportes'),
]