# sistemaTBC_demo/settings/base.py
"""
Configuración base común para todos los entornos
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================================================
# CORE DJANGO SETTINGS - REQUERIDOS PARA FUNCIONAMIENTO
# ============================================================================

# ¡IMPORTANTE! Esta configuración es CRÍTICA
ROOT_URLCONF = 'sistemaTBC_demo.urls'
WSGI_APPLICATION = 'sistemaTBC_demo.wsgi.application'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_spectacular',        
    'drf_spectacular_sidecar',
    
    # Project apps
    'apps.usuarios',
    'apps.pacientes',
    'apps.tratamientos',
    'apps.examenes',
    'apps.contactos',
    'apps.prevencion',
    'apps.laboratorio',
    'apps.indicadores',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'sistemaTBC_demo/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Para producción

# Directorios adicionales para archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Asegurar que Django encuentre los estáticos de drf-yasg
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# DATABASE CONFIGURATION - BASE PARA TODOS LOS ENTORNOS
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='sistema_tbc'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}

# ============================================================================
# REST FRAMEWORK CONFIGURATION - BASE
# ============================================================================

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # IMPORTANTE
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema TBC API',
    'DESCRIPTION': '''
    API RESTful completa para el Sistema de Gestión de Tuberculosis
    
    ## 📋 Características:
    - Gestión completa de pacientes con TBC
    - Seguimiento de tratamientos y medicamentos
    - Sistema de alertas y notificaciones
    - Integración con APIs externas (clima, geocodificación)
    - Dashboard con estadísticas en tiempo real
    
    ## 🔐 Autenticación:
    - Token-based authentication
    - Permisos por rol (Administrador, Médico, Enfermera, etc.)
    
    ## 📊 Endpoints disponibles:
    1. **/api/pacientes/** - CRUD completo de pacientes
    2. **/api/tratamientos/** - Gestión de tratamientos
    3. **/api/dashboard/** - Estadísticas y alertas
    4. **/api/external/** - APIs externas
    5. **/api/auth/** - Autenticación
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # UI configuration
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'showExtensions': True,
        'showCommonExtensions': True,
    },
    
    # Redoc settings
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
        'requiredPropsFirst': True,
    },
    
    # General settings
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    
    # Security
    'SECURITY': [{'Bearer': []}],
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token JWT en formato: Bearer <token>'
        }
    },
    
    # Tags
    'TAGS': [
        {'name': 'Pacientes', 'description': 'Gestión de pacientes con TBC'},
        {'name': 'Tratamientos', 'description': 'Gestión de tratamientos y medicamentos'},
        {'name': 'Dashboard', 'description': 'Estadísticas y alertas del sistema'},
        {'name': 'APIs Externas', 'description': 'Clima y geocodificación'},
        {'name': 'Autenticación', 'description': 'Login y tokens'},
    ],
}
# CORS settings (importante para Swagger)
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# O si prefieres una configuración más segura:
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# URL para redireccionar cuando se requiere login
LOGIN_URL = '/'

# URL a la que redirigir después del login exitoso
LOGIN_REDIRECT_URL = '/'

# URL a la que redirigir después del logout
LOGOUT_REDIRECT_URL = '/'
print("✓ Configuración base cargada")