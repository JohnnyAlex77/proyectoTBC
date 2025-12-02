
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
