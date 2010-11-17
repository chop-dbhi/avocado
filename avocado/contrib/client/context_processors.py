from django.conf import settings

def media(request):
    CLIENT_MEDIA_URL = getattr(settings, 'CLIENT_MEDIA_URL',
        settings.MEDIA_URL)
    CLIENT_JS_URL = getattr(settings, 'CLIENT_JS_URL', None)
    
    if CLIENT_JS_URL is None:
        SRC_DIR = getattr(settings, 'SRC_DIR', 'src')
        MIN_DIR = getattr(settings, 'MIN_DIR', 'min')
        _dir = settings.DEBUG and SRC_DIR or MIN_DIR
        CLIENT_JS_URL = '%sjs/%s/' % (CLIENT_MEDIA_URL, _dir)

    return {
        'CLIENT_MEDIA_URL': CLIENT_MEDIA_URL,
        'CLIENT_JS_URL': CLIENT_JS_URL
    }
