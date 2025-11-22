from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.lista_pacientes, name='lista'),
    path('crear/', views.crear_paciente, name='crear'),
    path('editar/<int:pk>/', views.editar_paciente, name='editar'),  
    path('detalle/<int:pk>/', views.detalle_paciente, name='detalle'),  
    path('eliminar/<int:pk>/', views.eliminar_paciente, name='eliminar'),  
    path('buscar/', views.buscar_pacientes, name='buscar'),
]