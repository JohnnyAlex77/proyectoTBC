# sistemaTBC_demo/context_processors.py
"""
Custom context processors for Sistema TBC
"""

def api_settings(request):
    '''
    Add API settings to template context
    '''
    from django.conf import settings
    
    return {
        'API_BASE_URL': getattr(settings, 'API_BASE_URL', '/api/'),
        'API_VERSION': getattr(settings, 'API_VERSION', 'v1'),
        'DEBUG': getattr(settings, 'DEBUG', False),
    }