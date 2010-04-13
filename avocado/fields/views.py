import re

from django.views.decorators.cache import never_cache
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils import simplejson
from django.utils import stopwords
from django.db.models import Q
from narwhal.utils.decorators import ajax_required
from avocado.criteria.datatypes import BadOperator
from avocado.exceptions import ValidationError
from .models import Field
from .cache import field_cache
from .utils import normalize_raw_data_for_avocado

def _format_criteria(sorted_dict):
    cached_criteria = []
    for key, val in sorted_dict.items():
        d = {
            'type': 'field',
            'id': key,
            'op': val['op'],
            'values': val['val'],
            'url': reverse('avocado-render-field', kwargs={'field_id': key}),
        }
        cached_criteria.append(d)
    return cached_criteria

@never_cache
@ajax_required('post')
def save_cached_fields(request):
    parsed_criteria = normalize_raw_data_for_avocado(request.POST)

    # set default dict with empty values
    if not request.session.has_key('cached_query'):
        cached_query = {
            'parsed_criteria': (),
            'set_id': None,
            'column_ids': (),
            'column_sortings': (),
            'count': 0,
            'unique_count': 0,
            'slice_index': 0,
            'rows': (),
            'force_new_query': True,
            'column_names': (),
            'formatter_names': (),
            'page': 1,
            'paginate_by': 10,
        }
        request.session['cached_query'] = cached_query
        request.session['cached_criteria'] = _format_criteria(parsed_criteria)
    else:
        cached_query = request.session['cached_query']

        if cached_query['parsed_criteria'] != parsed_criteria:
            cached_query['force_new_query'] = True
            request.session['cached_criteria'] = _format_criteria(parsed_criteria)

        cached_query['page'] = 1

    cached_query['parsed_criteria'] = parsed_criteria
    request.session.modified = True

    return HttpResponse()

@never_cache
@ajax_required
def fetch_cached_fields(request):
    field_states = request.session.get('cached_criteria', [])
    return HttpResponse(simplejson.dumps(field_states),
        mimetype='application/json')

@never_cache
@ajax_required
def render_field(request, field_id):
    if not request.is_ajax():
        raise Http404
    json = field_cache.get(field_id)
    return HttpResponse(json, mimetype='application/json')

@never_cache
@ajax_required
def validate_field(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    resp = {'success': False}

    op = request.GET.get('op')
    value = request.GET.getlist('value')

    try:
        field.datatype_cls.validate(op, value)
        resp['success'] = True
    except (ValidationError, BadOperator):
        pass

    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

@ajax_required('get')
def search(request):
    "Fulltext search on field meta data"
    fields = Field.objects.public()

    q = request.GET.get('q', None)
    if q:
        # get rid of non-alphanumerics, keep whitespace
        q = stopwords.strip_stopwords(q)
        toks = re.sub(r'[^\w\d\s-]+', '', q, re.I).split()

        for t in toks:
            fields = fields.filter(
                Q(display_name__icontains=t) |
                Q(allowed_values_fulltext__icontains=t) |
                Q(description__icontains=t) |
                Q(keywords__icontains=t))

    # check to see if user is apart of the `CanViewPhi' group to allow
    # access to the PHI fields
    if request.user.groups.filter(name='CanViewPHI').count() == 0:
        fields = fields.exclude(category__name='phi')

    fields = fields.select_related('category').order_by('category__name')

    t = get_template('avocado/fields/search.html')
    c = RequestContext(request, {
        'fields': fields
    })

    return HttpResponse(t.render(c))
