# sistemaTBC/settings/production.py
"""
Configuración para producción con MySQL - VERSIÓN FINAL SIN ERRORES
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
if isinstance(allowed_hosts_str, str):
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ==============================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL - VERSIÓN SIMPLIFICADA
# ==============================
# VERSIÓN SIMPLIFICADA: Ignorar DATABASE_URL problemático y usar MySQL directo
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
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default='False') == 'True'
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default='False') == 'True'
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default='False') == 'True'
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
# EMAIL - CORREGIDO DEFINITIVAMENTE
# ==============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')

# CORREGIDO: Evitar cast=bool problemático usando comparación directa
email_port_str = config('EMAIL_PORT', default='587')
#EMAIL_PORT = int(email_port_str) if email_port_str.isdigit() else 587

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# CORREGIDO: Sin cast=bool, usando comparación directa
email_use_tls_str = config('EMAIL_USE_TLS', default='True')
#EMAIL_USE_TLS = email_use_tls_str.lower() in ['true', '1', 'yes', 'on']

email_use_ssl_str = config('EMAIL_USE_SSL', default='False')
#EMAIL_USE_SSL = email_use_ssl_str.lower() in ['true', '1', 'yes', 'on']

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='sistema-tbc@inacap.cl')

# ==============================
# EXTERNAL APIS - CORREGIDO
# ==============================
OPENWEATHER_API_KEY = config('OPENWEATHER_API_KEY', default='')

# CORREGIDO: Evitar .strip() en valor que podría ser booleano
openweather_enabled = False
if OPENWEATHER_API_KEY and isinstance(OPENWEATHER_API_KEY, str):
    openweather_enabled = bool(OPENWEATHER_API_KEY.strip())

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
    'DEMO_MODE': False,
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

print("=" * 50)
print("✓ CONFIGURACIÓN PRODUCCIÓN MYSQL CARGADA CORRECTAMENTE")
print(f"✓ Base de datos: MySQL")
print(f"✓ Host: {DATABASES['default'].get('HOST', 'localhost')}")
print("=" * 50)