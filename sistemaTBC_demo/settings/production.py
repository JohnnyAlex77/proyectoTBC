# sistemaTBC_demo/settings/production.py
"""
Configuración para producción con MySQL - VERSIÓN FINAL CORREGIDA
"""
import os
from pathlib import Path
from decouple import config

# Definir BASE_DIR localmente
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================
# SEGURIDAD
# ==============================
DEBUG = False
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# ==============================
# ALLOWED_HOSTS - CORREGIDO
# ==============================
# CORREGIDO: Manejo seguro de ALLOWED_HOSTS
allowed_hosts_str = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in str(allowed_hosts_str).split(',')]

# ==============================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL
# ==============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='sistema_tbc'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 30,
        },
        'CONN_MAX_AGE': 600,
    }
}

print("✓ Usando configuración MySQL local")

# ==============================
# ARCHIVOS ESTÁTICOS
# ==============================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================
# SEGURIDAD HTTPS - CORREGIDO
# ==============================
# CORREGIDO: Usar valores por defecto seguros
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default='False', cast=lambda x: x == 'True')
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default='False', cast=lambda x: x == 'True')
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default='False', cast=lambda x: x == 'True')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if SECURE_SSL_REDIRECT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ==============================
# CORS
# ==============================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://sistema-tbc-api.onrender.com",
]
CORS_ALLOW_CREDENTIALS = True

# ==============================
# CACHE
# ==============================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ==============================
# LOGGING
# ==============================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_production.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

# Crear directorio de logs si no existe
log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# ==============================
# EMAIL - COMPLETAMENTE CORREGIDO
# ==============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')

# CORRECCIÓN: Asegurar que sea string antes de verificar isdigit()
email_port_value = config('EMAIL_PORT', default='587')
EMAIL_PORT = int(str(email_port_value)) if str(email_port_value).isdigit() else 587

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# CORRECCIÓN: Convertir a string y luego verificar
email_use_tls_value = config('EMAIL_USE_TLS', default='True')
EMAIL_USE_TLS = str(email_use_tls_value).lower() in ['true', '1', 'yes', 'on']

email_use_ssl_value = config('EMAIL_USE_SSL', default='False')
EMAIL_USE_SSL = str(email_use_ssl_value).lower() in ['true', '1', 'yes', 'on']

EMAIL_TIMEOUT = 30
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='sistema-tbc@inacap.cl')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

# ==============================
# EXTERNAL APIS - CORREGIDO
# ==============================
OPENWEATHER_API_KEY = config('OPENWEATHER_API_KEY', default='')

# CORRECCIÓN: Manejo seguro de tipo
openweather_enabled = False
if OPENWEATHER_API_KEY:
    api_key_str = str(OPENWEATHER_API_KEY)
    openweather_enabled = bool(api_key_str.strip()) if api_key_str else False

EXTERNAL_APIS = {
    'OPENWEATHERMAP': {
        'ENABLED': openweather_enabled,
        'API_KEY': OPENWEATHER_API_KEY,
        'BASE_URL': 'https://api.openweathermap.org/data/2.5',
        'TIMEOUT': 10,
        'CACHE_TIMEOUT': 1800,
    },
    'NOMINATIM': {
        'ENABLED': True,
        'BASE_URL': 'https://nominatim.openstreetmap.org',
        'TIMEOUT': 10,
        'USER_AGENT': 'SistemaTBC/1.0 (soporte@sistematbc.cl)',
        'CACHE_TIMEOUT': 86400,
    },
    'DEMO_MODE': config('API_DEMO_MODE', default='False', cast=lambda x: x == 'True'),
}

# ==============================
# REST FRAMEWORK
# ==============================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ==============================
# CONFIGURACIONES ADICIONALES IMPORTANTES
# ==============================
# Estas configuraciones están en tu settings.py viejo pero faltan aquí:

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'widget_tweaks',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'drf_yasg',
    
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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistemaTBC_demo.urls'
WSGI_APPLICATION = 'sistemaTBC_demo.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (adicionales)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'sistemaTBC_demo/static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

print("=" * 50)
print("✓ CONFIGURACIÓN PRODUCCIÓN MYSQL CARGADA CORRECTAMENTE")
print(f"✓ Base de datos: MySQL")
print(f"✓ Host: {DATABASES['default'].get('HOST', 'localhost')}")
print("=" * 50)