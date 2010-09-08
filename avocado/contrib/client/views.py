from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import select_template

def design(request):
    return render_to_response('design.html',
        context_instance=RequestContext(request))

def report(request):
    return render_to_response('report.html',
        context_instance=RequestContext(request))

# def design(request):
#     t = select_template(['design.html', 'client/design.html'])
#     c = RequestContext(request)
#     return HttpResponse(t.render(c))
# 
# def report(request):
#     t = select_template(['report.html', 'client/report.html'])
#     c = RequestContext(request)
#     return HttpResponse(t.render(c))