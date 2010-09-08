# from django.template import RequestContext
# from django.shortcuts import render_to_response, get_object_or_404
# from django.views.decorators.cache import never_cache
# 
# from production.models import PatientCohort
# from production.forms import PatientCohortForm
# 
# @never_cache
# def patient_set(request, set_id=None):
#     """Provides the initial view of a temporary or saved `PatientCohort'.
#     The only requirements here is to setup or fetch data that is required
#     by the template for UI components.
#     """
#     if not request.session.has_key('cached_query'):
#         cache = init_query_cache(request.user)
#         request.session['cached_query'] = cache
#     else:
#         cache = request.session.get('cached_query')
# 
#     if set_id is not None:
#         # if the same request, don't do the lookup
#         if not cache['set_obj'] or cache['set_obj'].id != set_id:
#             set_obj = get_object_or_404(PatientCohort, id=set_id, user=request.user)
#         else:
#             set_obj = cache['set_obj']
#     else:
#         set_obj = PatientCohort(user=request.user)
# 
#     patient_set_form = PatientCohortForm(instance=set_obj)
# 
#     cache['set_obj'] = set_obj
# 
#     request.session.modified = True
# 
#     columns = cache.column_concepts
#     columns = columns.select_related('category').order_by('category')
# 
#     column_ids = cache.column_ids
#     selected_columns = columns.filter(id__in=column_ids)
#     filtered_columns = columns.exclude(id__in=column_ids)
# 
#     ordered_columns = []
#     for pk in column_ids:
#         try:
#             col = selected_columns.get(pk=pk)
#             ordered_columns.append(col)
#         except columns.model.DoesNotExist:
#             continue
#     ordered_columns.extend(list(filtered_columns))
# 
#     return render_to_response('patient_sets/patient_set.html', {
#         'page': cache.page,
#         'columns': columns,
#         'selected_columns': ordered_columns,
#         'column_ids': column_ids,
#         'patient_set_form': patient_set_form,
#     }, context_instance=RequestContext(request))