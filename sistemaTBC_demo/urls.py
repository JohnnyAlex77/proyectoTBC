from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home/Login como página principal
    path('', LoginView.as_view(
        template_name='home/login.html',
        redirect_authenticated_user=True
    ), name='home'),
    
    # URLs de las aplicaciones
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('pacientes/', include('apps.pacientes.urls', namespace='pacientes')),
    path('contactos/', include('apps.contactos.urls', namespace='contactos')),
    path('examenes/', include('apps.examenes.urls', namespace='examenes')),
    path('tratamientos/', include('apps.tratamientos.urls', namespace='tratamientos')),
    path('prevencion/', include('apps.prevencion.urls', namespace='prevencion')),
    path('laboratorio/', include('apps.laboratorio.urls', namespace='laboratorio')),
    path('indicadores/', include('apps.indicadores.urls', namespace='indicadores')),
    
    # Redirección para usuarios autenticados
    path('inicio/', RedirectView.as_view(pattern_name='usuarios:dashboard'), name='inicio'),

    # API REST
    path('api/', include('api.urls')),
    
    # Documentación API
    path('api-docs/', include('api.urls')),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)