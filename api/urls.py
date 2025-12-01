# api/urls.py
"""
Configuración de URLs para las APIs del sistema TBC
Organiza endpoints internos y externos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Importar vistas
from api.views.pacientes import PacienteViewSet
from api.views.tratamientos import TratamientoViewSet, EsquemaMedicamentoViewSet
from api.views.dashboard import DashboardEstadisticasView, DashboardTendenciasView, DashboardAlertasView
from api.views.external import GeocodificarView, ClimaView, AnalisisEpidemiologicoView, api_status

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='pacientes')
router.register(r'tratamientos', TratamientoViewSet, basename='tratamientos')
router.register(r'esquemas-medicamento', EsquemaMedicamentoViewSet, basename='esquemas-medicamento')

# Configurar documentación Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Sistema TBC API",
        default_version='v1',
        description="API RESTful para el Sistema de Gestión de Tuberculosis",
        terms_of_service="https://www.sistematbc.cl/terms/",
        contact=openapi.Contact(email="soporte@sistematbc.cl"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    # Autenticación
    path('auth/token/', auth_views.obtain_auth_token, name='api_token_auth'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # APIs internas (CRUD)
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
    
    # Documentación
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]