from django.shortcuts import render_to_response
from django.template import RequestContext

def design(request):
    return render_to_response('design.html',
        context_instance=RequestContext(request))

def report(request):
    return render_to_response('report.html',
        context_instance=RequestContext(request))