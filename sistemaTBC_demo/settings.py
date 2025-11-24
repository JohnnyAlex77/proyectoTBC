"""
Django settings for sistematBC_demo project.
"""

from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY desde variables de entorno
SECRET_KEY = config('SECRET_KEY', default=get_random_secret_key())

# DEBUG=True para desarrollo
DEBUG = config('DEBUG', default=False, cast=bool)

# Hosts permitidos para desarrollo
ALLOWED_HOSTS = [
    '10.58.2.188',      # Tu IP
    '10.58.0.1',        # Puerta de enlace
    'localhost',
    '127.0.0.1',
    '.inacap.cl',       # Dominio INACAP
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'apps.pacientes',
    'apps.usuarios',
    'apps.contactos',
    'apps.tratamientos',
    'apps.examenes',
    'apps.prevencion',
    'apps.laboratorio',
    'apps.indicadores'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',# Headers de seguridad
    'django.contrib.sessions.middleware.SessionMiddleware',# Manejo de sesiones
    'django.middleware.common.CommonMiddleware',# Normalizacion de URLs
    'django.middleware.csrf.CsrfViewMiddleware',# Proteccion CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',# Autenticacion de usuarios
    'django.contrib.messages.middleware.MessageMiddleware',# Sistema de mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware',# Proteccion clickjacking
]

ROOT_URLCONF = 'sistemaTBC_demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'sistemaTBC_demo/templates'], 
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

WSGI_APPLICATION = 'sistemaTBC_demo.wsgi.application'

# Configuración de base de datos con variables de entorno
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# CONFIGURACION DE AUTENTICACION Y SEGURIDAD
# Backend de autenticacion por defecto de Django
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Algoritmos de hashing para contraseñas
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',# Algoritmo por defecto con 260,000 iteraciones
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',# Alternativa compatible
    'django.contrib.auth.hashers.Argon2PasswordHasher',# Algoritmo moderno más seguro
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',# Alternativa ampliamente usada
]

# CONFIGURACION DE SESIONES

# Tiempo de vida de la sesion en segundos (1 hora de inactividad)
SESSION_COOKIE_AGE = 3600
# La sesion expira al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Solo enviar cookies de sesion por HTTPS (False en desarrollo, True en produccion)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
# Proteccion contra acceso via JavaScript
SESSION_COOKIE_HTTPONLY = True
# Nombre personalizado de la cookie de sesion
SESSION_COOKIE_NAME = 'sistematbc_sessionid'
# Motor de almacenamiento de sesiones (base de datos)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Guardar sesion en cada request para actualizar timeout
SESSION_SAVE_EVERY_REQUEST = True

# CONFIGURACION DE SEGURIDAD CSRF

# Solo enviar cookies CSRF por HTTPS (False en desarrollo, True en produccion)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
# Permitir acceso a cookie CSRF via JavaScript (necesario para AJAX)
CSRF_COOKIE_HTTPONLY = False
# Politica SameSite para cookies CSRF
CSRF_COOKIE_SAMESITE = 'Lax'
# No usar sesiones para almacenar tokens CSRF
CSRF_USE_SESSIONS = False
# Vista personalizada para fallos CSRF
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# HEADERS DE SEGURIDAD

# Filtro XSS para navegadores compatibles
SECURE_BROWSER_XSS_FILTER = True
# Prevenir sniffing de tipo MIME
SECURE_CONTENT_TYPE_NOSNIFF = True
# Proteccion contra clickjacking
X_FRAME_OPTIONS = 'DENY'

# CONFIGURACION INTERNACIONAL

# Configuracion regional para Chile
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# CONFIGURACION DE ARCHIVOS ESTATICOS

# URL base para archivos estaticos
STATIC_URL = '/static/'
# Directorio donde se recolectan archivos estaticos en produccion
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Directorios adicionales para archivos estaticos
static_dir = os.path.join(BASE_DIR, 'static')
if os.path.exists(static_dir):
    # Verificar que no exista carpeta admin que cause conflictos
    admin_static_dir = os.path.join(static_dir, 'admin')
    if os.path.exists(admin_static_dir):
        print(f"ADVERTENCIA: Carpeta {admin_static_dir} existe. Puede causar conflictos.")
    
    STATICFILES_DIRS = [static_dir]
else:
    STATICFILES_DIRS = []

# CONFIGURACIONES GENERALES

# Tipo de campo primario por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuracion de etiquetas para mensajes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# URLS DE AUTENTICACION

# URL para redireccionar cuando se requiere login
LOGIN_URL = '/'
# URL a la que redirigir despues del login exitoso
LOGIN_REDIRECT_URL = '/usuarios/dashboard/'
# URL a la que redirigir despues del logout
LOGOUT_REDIRECT_URL = '/'

# CONFIGURACION ESPECIFICA PARA DESARROLLO

if DEBUG:
    # Deshabilitar seguridad estricta en desarrollo
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    
    # Configuracion de logging para desarrollo
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django.security': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

# Configuracion adicional para MySQL
if 'mysql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS']['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1"