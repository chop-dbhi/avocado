from django.utils import simplejson
from django.http import HttpResponse
from avocado.columns.models import ColumnConcept

def search(request):
    # limit columns to what the user can see
    groups = request.user.groups.all()
    columns = ColumnConcept.objects.restrict_by_group(groups)
    
    search_str = request.GET.get('q', None)
    if search_str:
        columns = ColumnConcept.objects.fulltext_search(search_str, columns,
            use_icontains=True)

    json = {'column_ids': [c.id for c in columns]}
    
    return HttpResponse(simplejson.dumps(json), mimetype='application/json')