# apps/contactos/urls.py
from django.urls import path
from . import views

app_name = 'contactos'

urlpatterns = [
    path('', views.lista_contactos, name='lista'),
    path('crear/', views.crear_contacto, name='crear'),
    path('editar/<int:pk>/', views.editar_contacto, name='editar'),
    path('detalle/<int:pk>/', views.detalle_contacto, name='detalle'),
    path('eliminar/<int:pk>/', views.eliminar_contacto, name='eliminar'),
    path('buscar/', views.buscar_contactos, name='buscar'),
    path('buscar-pacientes-ajax/', views.buscar_pacientes_ajax, name='buscar_pacientes_ajax'),
]