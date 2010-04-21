from django.utils import simplejson
from django.http import HttpResponse
from narwhal.utils.decorators import ajax_required
from avocado.columns.models import ColumnConcept

def search(request):
    # limit columns to what the user can see
    groups = request.user.groups.all()
    columns = ColumnConcept.objects.restrict_by_group(groups)
    
    search_str = request.GET.get('q', None)
    if search_str:
        columns = ColumnConcept.objects.fulltext(search_str, columns)

    json = {'column_ids': [c.id for c in columns]}
    
    return HttpResponse(simplejson.dumps(json), mimetype='application/json')