"""
Django settings for sistemaTBC_demo project.
Configuración completa para sistema TBC con APIs RESTful
"""

from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# SECRET_KEY desde variables de entorno
SECRET_KEY = config('SECRET_KEY', default=get_random_secret_key())

# DEBUG=True para desarrollo, False para producción
DEBUG = config('DEBUG', default=False, cast=bool)

# Hosts permitidos para desarrollo y producción
ALLOWED_HOSTS = [
    # Desarrollo local
    'localhost',
    '127.0.0.1',
    
    # Redes internas INACAP
    '10.58.2.188',      # Tu IP
    '10.58.0.1',        # Puerta de enlace
    '.inacap.cl',       # Dominio INACAP
    
    # Producción (Render/Cloudflare)
    '.onrender.com',
    '.vercel.app',
    '.up.railway.app',
    
    # Permitir cualquier host en desarrollo
    '*' if DEBUG else '',
]

# ============================================================================
# APPLICATION DEFINITION
# ============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'widget_tweaks',
    
    # Django REST Framework y dependencias
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'drf_yasg',
    
    # Project apps (core modules)
    'apps.usuarios',
    'apps.pacientes',
    'apps.tratamientos',
    'apps.examenes',
    'apps.contactos',
    'apps.prevencion',
    'apps.laboratorio',
    'apps.indicadores',
    
    # API application
    'api',
]

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

MIDDLEWARE = [
    # CORS debe ir primero
    'corsheaders.middleware.CorsMiddleware',
    
    # Security middleware
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Session middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Common middleware
    'django.middleware.common.CommonMiddleware',
    
    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Messages
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================

REST_FRAMEWORK = {
    # Authentication settings
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    
    # Permission settings
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination settings
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Filter settings
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Renderer settings (JSON por defecto, HTML para navegador)
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    
    # Parser settings
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    
    # Throttling settings (protección contra ataques)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    
    # Versioning
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    
    # Metadata
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    
    # Exception handling
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # Content negotiation
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rest_framework.negotiation.DefaultContentNegotiation',
    
    # Schema generation
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
}

# ============================================================================
# CORS CONFIGURATION (Cross-Origin Resource Sharing)
# ============================================================================

# Configuración CORS para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Permitir credenciales (cookies, headers de autenticación)
CORS_ALLOW_CREDENTIALS = True

# Headers permitidos en CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Métodos HTTP permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# URLs que no requieren CORS (opcional)
CORS_URLS_REGEX = r'^/api/.*$'

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    },
    
    # Cache para APIs externas
    'api_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api-cache',
        'TIMEOUT': 1800,  # 30 minutos para datos de APIs externas
        'OPTIONS': {
            'MAX_ENTRIES': 500
        }
    },
}

# Tiempos de cache específicos para APIs
API_CACHE_TIMEOUTS = {
    'geocoding': 86400,      # 24 horas
    'weather': 1800,         # 30 minutos
    'dashboard': 300,        # 5 minutos
    'patients': 60,          # 1 minuto
}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

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
        'CONN_MAX_AGE': 600,  # Reutilizar conexiones por 10 minutos
        'TEST': {
            'NAME': 'test_sistema_tbc',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# Configuración adicional para MySQL
if 'mysql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'].update({
        'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION',
        'isolation_level': 'read committed',
    })

# ============================================================================
# TEMPLATE CONFIGURATION
# ============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'sistemaTBC_demo/templates',
            BASE_DIR / 'templates',  # Para templates de API
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processors
                'sistemaTBC_demo.context_processors.api_settings',
            ],
            'libraries': {
                'api_filters': 'api.templatetags.api_filters',
            },
        },
    },
]

# ============================================================================
# WSGI/ASGI CONFIGURATION
# ============================================================================

WSGI_APPLICATION = 'sistemaTBC_demo.wsgi.application'

# Para futura implementación de WebSockets
ASGI_APPLICATION = 'sistemaTBC_demo.asgi.application'

# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================

# Backend de autenticación por defecto de Django
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
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

# Tiempo de vida de la sesión en segundos (1 hora de inactividad)
SESSION_COOKIE_AGE = 3600

# La sesión expira al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Solo enviar cookies de sesión por HTTPS (False en desarrollo, True en producción)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)

# Protección contra acceso via JavaScript
SESSION_COOKIE_HTTPONLY = True

# Nombre personalizado de la cookie de sesión
SESSION_COOKIE_NAME = 'sistematbc_sessionid'

# Motor de almacenamiento de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Guardar sesión en cada request para actualizar timeout
SESSION_SAVE_EVERY_REQUEST = True

# Dominio para cookies de sesión
SESSION_COOKIE_DOMAIN = config('SESSION_COOKIE_DOMAIN', default=None)

# ============================================================================
# CSRF CONFIGURATION
# ============================================================================

# Solo enviar cookies CSRF por HTTPS
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# Permitir acceso a cookie CSRF via JavaScript (necesario para AJAX)
CSRF_COOKIE_HTTPONLY = False

# Política SameSite para cookies CSRF
CSRF_COOKIE_SAMESITE = 'Lax'

# No usar sesiones para almacenar tokens CSRF
CSRF_USE_SESSIONS = False

# Vista personalizada para fallos CSRF
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Trusted origins para CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'https://*.onrender.com',
    'https://*.inacap.cl',
]

# ============================================================================
# SECURITY HEADERS
# ============================================================================

# Filtro XSS para navegadores compatibles
SECURE_BROWSER_XSS_FILTER = True

# Prevenir sniffing de tipo MIME
SECURE_CONTENT_TYPE_NOSNIFF = True

# Protección contra clickjacking
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 año en producción
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Redirect HTTP a HTTPS (en producción)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Locales disponibles
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ============================================================================
# STATIC FILES CONFIGURATION
# ============================================================================

# URL base para archivos estáticos
STATIC_URL = '/static/'

# Directorio donde se recolectan archivos estáticos en producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Directorios adicionales para archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'sistemaTBC_demo/static',
]

# Motor de almacenamiento para archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise configuration
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# ============================================================================
# MEDIA FILES CONFIGURATION
# ============================================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# Tipos de archivos permitidos para upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_TIMEOUT = 30

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='sistema-tbc@inacap.cl')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

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
        'api_format': {
            'format': '{asctime} - {name} - {levelname} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose'
        },
        'api_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/api.log',
            'formatter': 'api_format'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'api_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api.external': {
            'handlers': ['api_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
if not os.path.exists(BASE_DIR / 'logs'):
    os.makedirs(BASE_DIR / 'logs')

# ============================================================================
# CUSTOM SETTINGS
# ============================================================================

# Tipo de campo primario por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de etiquetas para mensajes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ============================================================================
# AUTHENTICATION URLs
# ============================================================================

# URL para redireccionar cuando se requiere login
LOGIN_URL = '/'

# URL a la que redirigir después del login exitoso
LOGIN_REDIRECT_URL = '/usuarios/dashboard/'

# URL a la que redirigir después del logout
LOGOUT_REDIRECT_URL = '/'

# ============================================================================
# API SPECIFIC SETTINGS
# ============================================================================

# API Documentation (Swagger/Redoc)
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token de autenticación en formato: Token <tu_token>'
        },
        'Basic': {
            'type': 'basic',
            'description': 'Autenticación básica con usuario y contraseña'
        }
    },
    'USE_SESSION_AUTH': True,
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    'DEFAULT_INFO': 'api.urls.schema_view',
    'DEFAULT_API_URL': None,
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.JSONFieldInspector',
        'drf_yasg.inspectors.HiddenFieldInspector',
        'drf_yasg.inspectors.RecursiveFieldInspector',
        'drf_yasg.inspectors.SerializerMethodFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'EXCLUDED_MEDIA_TYPES': [],
    'VALIDATOR_URL': '',
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,
    'FETCH_SCHEMA_WITH_QUERY': True,
    'OPERATIONS_SORTER': None,
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': False,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_DEPTH': 3,
    'SHOW_COMMON_EXTENSIONS': True,
    'OAUTH2_REDIRECT_URL': None,
    'OAUTH2_CONFIG': {},
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'put',
        'post',
        'delete',
        'options',
        'head',
        'patch',
        'trace'
    ],
}

# Redoc settings
REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': False,
    'NATIVE_SCROLLBARS': False,
    'REQUIRED_PROPS_FIRST': True,
    'SORT_OPERATION_TAGS': True,
    'SORT_OPERATIONS': True,
    'SORT_TAGS': True,
    'NO_AUTO_AUTH': False,
    'THEME': {
        'spacing': {
            'unit': 4,
            'sectionVertical': 16
        },
        'breakpoints': {
            'small': '50rem',
            'medium': '85rem',
            'large': '105rem'
        },
        'colors': {
            'primary': {
                'main': '#32329f'
            },
            'text': {
                'primary': '#151515'
            }
        },
        'typography': {
            'fontFamily': '"Roboto", "Helvetica Neue", Helvetica, Arial, sans-serif',
            'fontSize': '14px',
            'lineHeight': '1.5em',
            'fontWeightRegular': '400',
            'fontWeightBold': '600',
            'fontWeightLight': '300',
            'headings': {
                'fontFamily': '"Roboto", "Helvetica Neue", Helvetica, Arial, sans-serif',
                'fontWeight': '600'
            },
            'code': {
                'fontFamily': '"Source Code Pro", monospace',
                'fontSize': '13px',
                'fontWeight': '400',
                'color': '#e53935',
                'backgroundColor': 'rgba(38, 50, 56, 0.05)'
            },
            'links': {
                'color': '#32329f',
                'visited': '#5e35b1',
                'hover': '#1a237e'
            }
        },
        'sidebar': {
            'width': '260px',
            'backgroundColor': '#fafafa',
            'textColor': '#151515'
        },
        'rightPanel': {
            'backgroundColor': '#263238',
            'textColor': '#ffffff',
            'width': '40%'
        }
    }
}

# API Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_CACHE_PREFIX = 'rl:'
RATELIMIT_VIEW = 'api.views.api_limiter_exceeded'

# External APIs configuration
EXTERNAL_APIS = {
    'OPENWEATHERMAP': {
        'ENABLED': True,
        'API_KEY': config('OPENWEATHERMAP_API_KEY', default=''),
        'BASE_URL': 'https://api.openweathermap.org/data/2.5',
        'TIMEOUT': 10,
        'CACHE_TIMEOUT': 1800,  # 30 minutes
    },
    'NOMINATIM': {
        'ENABLED': True,
        'BASE_URL': 'https://nominatim.openstreetmap.org',
        'TIMEOUT': 10,
        'USER_AGENT': 'SistemaTBC/1.0 (soporte@sistematbc.cl)',
        'CACHE_TIMEOUT': 86400,  # 24 hours
    },
    'DEMO_MODE': config('API_DEMO_MODE', default=DEBUG, cast=bool),
}

# API Version
API_VERSION = 'v1'
API_BASE_URL = '/api/'

# ============================================================================
# PRODUCTION SPECIFIC SETTINGS
# ============================================================================

if not DEBUG:
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Content Security Policy (CSP) - ajustar según necesidades
    # MIDDLEWARE.insert(0, 'csp.middleware.CSPMiddleware')
    
    # Database connection pooling for production
    DATABASES['default']['CONN_MAX_AGE'] = 600
    DATABASES['default']['OPTIONS']['pool'] = {
        'max_overflow': 10,
        'pool_size': 5,
        'recycle': 300,
    }
    
    # Cache para producción (usar Redis si está disponible)
    redis_url = config('REDIS_URL', default=None)
    if redis_url:
        CACHES['default'] = {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 100},
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'KEY_PREFIX': 'sistematbc',
            'TIMEOUT': 300,
        }
    
    # Logging para producción
    LOGGING['handlers']['file']['level'] = 'ERROR'
    LOGGING['handlers']['mail_admins']['level'] = 'ERROR'
    
    # Email configuration for production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
    # CORS para producción
    CORS_ALLOWED_ORIGINS = [
        'https://sistema-tbc.onrender.com',
        'https://sistematbc.cl',
        'https://www.sistematbc.cl',
    ]
    
    # Allowed hosts for production
    ALLOWED_HOSTS = [
        'sistema-tbc.onrender.com',
        'sistematbc.cl',
        'www.sistematbc.cl',
        '.inacap.cl',
    ]

# ============================================================================
# DEVELOPMENT SPECIFIC SETTINGS
# ============================================================================

if DEBUG:
    # Deshabilitar seguridad estricta en desarrollo
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    
    # CORS más permisivo en desarrollo
    CORS_ALLOW_ALL_ORIGINS = True
    
    # Extras para desarrollo
    INSTALLED_APPS += [
        'debug_toolbar',
        'django_browser_reload',
    ]
    
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'django_browser_reload.middleware.BrowserReloadMiddleware',
    ] + MIDDLEWARE
    
    # Debug toolbar settings
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'RESULTS_CACHE_SIZE': 100,
        'SHOW_COLLAPSED': True,
        'SQL_WARNING_THRESHOLD': 100,
    }
    
    # Internal IPs for debug toolbar
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
        '10.58.2.188',
        '10.58.0.1',
    ]
    
    # Django extensions
    SHELL_PLUS = "ipython"
    SHELL_PLUS_PRINT_SQL = True
    SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000
    
    # Logging más detallado en desarrollo
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    LOGGING['loggers']['api']['level'] = 'DEBUG'

# ============================================================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================================================

# Validar variables críticas
required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD']
for var in required_vars:
    if not config(var, default=''):
        if DEBUG:
            print(f"Advertencia: Variable {var} no configurada")
        else:
            raise ValueError(f"Variable {var} requerida no configurada")

# ============================================================================
# CUSTOM CONTEXT PROCESSORS
# ============================================================================

# Crear archivo context_processors.py si no existe
context_processors_path = BASE_DIR / 'sistemaTBC_demo' / 'context_processors.py'
if not context_processors_path.exists():
    with open(context_processors_path, 'w') as f:
        f.write("""
'''
Custom context processors for Sistema TBC
'''

def api_settings(request):
    '''
    Add API settings to template context
    '''
    from django.conf import settings
    
    return {
        'API_BASE_URL': settings.API_BASE_URL,
        'API_VERSION': settings.API_VERSION,
        'API_DEMO_MODE': settings.EXTERNAL_APIS.get('DEMO_MODE', False),
        'DEBUG': settings.DEBUG,
    }
""")

# ============================================================================
# FINAL VALIDATION
# ============================================================================

# Validar que los directorios necesarios existan
required_dirs = [
    BASE_DIR / 'static',
    BASE_DIR / 'media',
    BASE_DIR / 'logs',
    BASE_DIR / 'templates',
]

for dir_path in required_dirs:
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        if DEBUG:
            print(f"Directorio creado: {dir_path}")

print(f"""
================================================================
SISTEMA TBC API CONFIGURADO
================================================================
Modo: {'DESARROLLO' if DEBUG else 'PRODUCCIÓN'}
API Base: {API_BASE_URL}{API_VERSION}/
Database: {DATABASES['default']['ENGINE']}
Debug: {DEBUG}
Allowed Hosts: {ALLOWED_HOSTS[:3]}...
================================================================
""")