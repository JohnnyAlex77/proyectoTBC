# apps/tratamientos/urls.py
from django.urls import path
from . import views

app_name = 'tratamientos'

urlpatterns = [
    # Tratamientos
    path('', views.lista_tratamientos, name='lista'),
    path('crear/', views.crear_tratamiento, name='crear'),
    path('<int:pk>/', views.detalle_tratamiento, name='detalle'),
    path('<int:pk>/editar/', views.editar_tratamiento, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_tratamiento, name='eliminar'),
    
    # Esquemas de Medicamento
    path('<int:tratamiento_pk>/esquema/crear/', views.crear_esquema_medicamento, name='crear_esquema'),
    path('esquema/<int:pk>/eliminar/', views.eliminar_esquema_medicamento, name='eliminar_esquema'),
    
    # Dosis Administradas
    path('esquema/<int:esquema_pk>/dosis/registrar/', views.registrar_dosis, name='registrar_dosis'),
    path('dosis/pendientes/', views.lista_dosis_pendientes, name='dosis_pendientes'),
    path('control-dosis/', views.control_dosis, name='control_dosis'),
    path('calendario/', views.calendario_dosis, name='calendario_dosis'),
    
    # Búsqueda AJAX
    path('buscar-paciente/', views.buscar_paciente_por_rut, name='buscar_paciente'),
    path('verificar-tratamiento/<int:paciente_id>/', views.verificar_paciente_tratamiento_activo, name='verificar_tratamiento'),
    
    # Debug temporal
    path('debug-pacientes/', views.debug_pacientes, name='debug_pacientes'),
]