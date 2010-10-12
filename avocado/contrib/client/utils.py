import re

IP_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

def get_ip_address(request):
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
        request.META.get('REMOTE_ADDR', None))
    
    if ip_address:
        ip_match = IP_RE.match(ip_address)
        if ip_match is not None:
            ip_address = ip_match.group()
        else:
            ip_address = None
    return ip_address