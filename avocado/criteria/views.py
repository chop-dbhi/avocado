from django.http import HttpResponse

from avocodo.criteria.cache import cache

def concept_views(request, concept_id):
    concept = cache.get(concept_id)
    return HttpResponse()