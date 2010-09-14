from django.conf import settings

def media(request):
    media_url = getattr(settings, 'CLIENT_MEDIA_URL', settings.MEDIA_URL)
    js_url = getattr(settings, 'CLIENT_JS_URL', media_url + 'js/')
    return {
        'CLIENT_MEDIA_URL': media_url,
        'CLIENT_JS_URL': js_url
    }
