from django.urls import path
from . import views

app_name = 'prevencion'

urlpatterns = [
    # Quimioprofilaxis
    path('quimioprofilaxis/', views.QuimioprofilaxisListView.as_view(), name='quimioprofilaxis_lista'),
    path('quimioprofilaxis/crear/', views.QuimioprofilaxisCreateView.as_view(), name='quimioprofilaxis_crear'),
    path('quimioprofilaxis/<int:pk>/editar/', views.QuimioprofilaxisUpdateView.as_view(), name='quimioprofilaxis_editar'),
    path('quimioprofilaxis/<int:pk>/', views.QuimioprofilaxisDetailView.as_view(), name='quimioprofilaxis_detalle'),
    path('quimioprofilaxis/<int:pk>/eliminar/', views.QuimioprofilaxisDeleteView.as_view(), name='quimioprofilaxis_eliminar'),
    
    # Vacunacion BCG
    path('vacunacion/', views.VacunacionBCGListView.as_view(), name='vacunacion_lista'),
    path('vacunacion/crear/', views.VacunacionBCGCreateView.as_view(), name='vacunacion_crear'),
    
    # Seguimientos
    path('seguimiento/crear/', views.SeguimientoCreateView.as_view(), name='seguimiento_crear'),
    
    # AJAX endpoints
    path('buscar-paciente-contacto/', views.buscar_paciente_contacto_ajax, name='buscar_paciente_contacto_ajax'),
]