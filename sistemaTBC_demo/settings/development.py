# sistemaTBC_demo/settings/development.py
"""
Configuración para desarrollo local
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-develop-key-123456-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.58.2.188']

# Database
# Usar SQLite para desarrollo más rápido si se desea
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': BASE_DIR / 'db.sqlite3',
# }

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS más permisivo en desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar
#INSTALLED_APPS += ['debug_toolbar']
#MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Logging para desarrollo
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
}

# URL para redireccionar cuando se requiere login
LOGIN_URL = '/'

# URL a la que redirigir después del login exitoso
LOGIN_REDIRECT_URL = '/usuarios/dashboard/'

# URL a la que redirigir después del logout
LOGOUT_REDIRECT_URL = '/'

print("✓ Configuración de desarrollo cargada")