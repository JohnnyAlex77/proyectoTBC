# apps/examenes/urls.py
from django.urls import path
from . import views

app_name = 'examenes'

urlpatterns = [
    path('', views.lista_examenes, name='lista_examenes'),
    path('crear/', views.crear_examen, name='crear_examen'),
    path('<int:examen_id>/', views.detalle_examen, name='detalle_examen'),
    path('<int:examen_id>/editar/', views.editar_examen, name='editar_examen'),
    path('<int:examen_id>/eliminar/', views.eliminar_examen, name='eliminar_examen'),
    path('paciente/<int:paciente_id>/', views.examenes_por_paciente, name='examenes_por_paciente'),
    
    # APIs para búsquedas AJAX
    path('buscar-paciente-rut/', views.buscar_paciente_por_rut, name='buscar_paciente_rut'),
    path('buscar-laboratorio/', views.buscar_laboratorio_por_nombre, name='buscar_laboratorio'),
]