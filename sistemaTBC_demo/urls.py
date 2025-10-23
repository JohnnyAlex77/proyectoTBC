from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('pacientes/', include('apps.pacientes.urls', namespace='pacientes')),
    path('contactos/', include('apps.contactos.urls', namespace='contactos')),

    
]