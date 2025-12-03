"""
Configuración de URLs para las APIs del sistema TBC
Usando drf-spectacular para documentación
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Importar vistas
from api.views.pacientes import PacienteViewSet
from api.views.tratamientos import TratamientoViewSet
from api.views.dashboard import DashboardEstadisticasView, DashboardTendenciasView, DashboardAlertasView
from api.views.external import GeocodificarView, ClimaView, AnalisisEpidemiologicoView, api_status

# Configurar router
router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='pacientes')
router.register(r'tratamientos', TratamientoViewSet, basename='tratamientos')

urlpatterns = [
    # =====================
    # AUTENTICACIÓN
    # =====================
    path('auth/token/', auth_views.obtain_auth_token, name='api_token_auth'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # =====================
    # APIS INTERNAS (CRUD)
    # =====================
    path('', include(router.urls)),
    
    # Dashboard y estadísticas
    path('dashboard/estadisticas/', DashboardEstadisticasView.as_view(), name='dashboard-estadisticas'),
    path('dashboard/tendencias/', DashboardTendenciasView.as_view(), name='dashboard-tendencias'),
    path('dashboard/alertas/', DashboardAlertasView.as_view(), name='dashboard-alertas'),
    
    # APIs externas
    path('external/geocodificar/', GeocodificarView.as_view(), name='api-geocodificar'),
    path('external/clima/', ClimaView.as_view(), name='api-clima'),
    path('external/analisis-epidemiologico/', AnalisisEpidemiologicoView.as_view(), name='api-analisis-epidemiologico'),
    
    # Utilidades
    path('status/', api_status, name='api-status'),
    
    # =====================
    # DOCUMENTACIÓN CON DRF-SPECTACULAR
    # =====================
    
    # Esquema OpenAPI en YAML/JSON
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI - Interfaz interactiva
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc - Documentación alternativa
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # =====================
    # ALIASES PARA COMPATIBILIDAD
    # =====================
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alt'),
    path('redoc-ui/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-alt'),
]