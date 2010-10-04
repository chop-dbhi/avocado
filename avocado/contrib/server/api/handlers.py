from datetime import datetime

from django.core.exceptions import (ObjectDoesNotExist, MultipleObjectsReturned,
    PermissionDenied)
from piston.handler import BaseHandler
from piston.utils import rc

from avocado.models import Category, Scope, Perspective, Report, Column
from avocado.contrib.server.api.models import CriterionProxy
from avocado.conf import settings

def convert2str(data):
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, dict):
        return dict(map(convert2str, data.iteritems()))
    elif isinstance(data, (list, tuple, set, frozenset)):
        return type(data)(map(convert2str, data))
    else:
        return data

class CategoryHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Category
    fields = ('id', 'name')


class CriterionHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = CriterionProxy

    def queryset(self, request):
        "Overriden to allow for user specificity."
        # restrict_by_group only in effect when FIELD_GROUP_PERMISSIONS is
        # enabled
        if settings.FIELD_GROUP_PERMISSIONS:
            groups = request.user.groups.all()
            return self.model.objects.restrict_by_group(groups)
        return self.model.objects.public()

    def read(self, request, *args, **kwargs):
        obj = super(CriterionHandler, self).read(request, *args, **kwargs)
        # if an instance was returned, simply return the view responses
        if isinstance(obj, self.model):
            return obj.view_responses()

        # apply fulltext if the 'q' GET param exists
        if request.GET.has_key('q'):
            obj = self.model.objects.fulltext_search(request.GET.get('q'), obj, True)
        return map(lambda x: x.json(), obj)


class ColumnHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Column
    fields = ('id', 'name', 'description')

    def queryset(self, request):
        "Overriden to allow for user specificity."
        # restrict_by_group only in effect when FIELD_GROUP_PERMISSIONS is
        # enabled
        if settings.FIELD_GROUP_PERMISSIONS:
            groups = request.user.groups.all()
            return self.model.objects.restrict_by_group(groups)
        return self.model.objects.public()

    def read(self, request, *args, **kwargs):
        obj = super(ColumnHandler, self).read(request, *args, **kwargs)

        # apply fulltext if the 'q' GET param exists
        if request.GET.has_key('q'):
            obj = self.model.objects.fulltext_search(request.GET.get('q'), obj, True)
        return obj


class ScopeHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    model = Scope
    fields = ('store',)

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        """Modified to allow for requesting the session's current ``scope``.

        The override specifies the kwarg ``id`` with a value "session" instead
        of the primary key.
        """

        if kwargs.get('id', None) != 'session':
            return super(ScopeHandler, self).read(request, *args, **kwargs)
        return request.session['report'].scope


    def update(self, request, *args, **kwargs):
        """Modified to allow for updating the session's current ``scope``
        object.

        If the session's current ``scope`` is not temporary, it will be
        copied and store off temporarily.
        """
        # perform default behavior of responding with rc.BAD_REQUEST
        if not kwargs.has_key('id'):
            super(ScopeHandler, self).update(request, *args, **kwargs)

        # if the request is relative to the session and not to a specific id,
        # it cannot be assumed that if the session is using a saved scope
        # for it, iself, to be updated, but rather the session representation.
        # therefore, if the session scope is not temporary, make it a
        # temporary object with the new parameters.
        inst = request.session['report'].scope

        json = convert2str(request.data)

        # see if the json object is only the ``store``
        if 'children' in json or 'operator' in json:
            json = {'store': json}

        # assume the PUT request is only the store
        if kwargs['id'] != 'session':
            if kwargs['id'] != inst.id:
                try:
                    inst = self.queryset(request).get(pk=kwargs['id'])
                except ObjectDoesNotExist:
                    return rc.NOT_FOUND
                except MultipleObjectsReturned:
                    return rc.BAD_REQUEST

        store = json.pop('store', None)

        if store is not None:
            if not inst.is_valid(store) or inst.has_permission(store, request.user):
                rc.BAD_REQUEST
            inst.write(store)

        attrs = self.flatten_dict(json)
        for k, v in attrs.iteritems():
            setattr(inst, k, v)

        # only save existing instances that have been saved.
        # a POST is required to make the intial save
        if inst.id is not None:
            inst.save()

        request.session['report'].scope = inst
        request.session.modified = True

        return rc.ALL_OK


class PerspectiveHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    model = Perspective
    fields = ('store',)

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        """Modified to allow for requesting the session's current
        ``perspective``.

        The override specifies the kwarg ``id`` with a value "session" instead
        of the primary key.
        """
        if kwargs.get('id', None) != 'session':
            return super(PerspectiveHandler, self).read(request, *args, **kwargs)
        return request.session.get('report').perspective

    def update(self, request, *args, **kwargs):
        """Modified to allow for updating the session's current ``perspective``
        object.

        If the session's current ``perspective`` is not temporary, it will be
        copied and store off temporarily.
        """
        # perform default behavior of responding with rc.BAD_REQUEST
        if not kwargs.has_key('id'):
            super(PerspectiveHandler, self).update(request, *args, **kwargs)

        # if the request is relative to the session and not to a specific id,
        # it cannot be assumed that if the session is using a saved perspective
        # for it, iself, to be updated, but rather the session representation.
        # therefore, if the session perspective is not temporary, make it a
        # temporary object with the new parameters.
        json = convert2str(request.data)
        inst = request.session['report'].perspective

        try:
            inst.has_permission(json, request.user)
        except PermissionDenied:
            return rc.FORBIDDEN

        # assume the PUT request is only the store
        if kwargs['id'] == 'session':
            inst.write(json)

        # an object has been targeted via the ``id`` referenced in the url
        else:
            if int(kwargs['id']) != inst.id:
                try:
                    inst = self.queryset(request).get(pk=kwargs['id'])
                except ObjectDoesNotExist:
                    return rc.NOT_FOUND
                except MultipleObjectsReturned:
                    return rc.BAD_REQUEST

            store = json.pop('store', None)
            attrs = self.flatten_dict(json)

            # special case
            if store is not None:
                inst.write(store)

            for k, v in attrs.iteritems():
                setattr(inst, k, v)

            inst.save()

        request.session['report'].perspective = inst
        request.session.modified = True

        return rc.ALL_OK


class ReportHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Report
    fields = (
        ('scope', ScopeHandler.fields),
        ('perspective', PerspectiveHandler.fields)
    )
#    exclude = ('user',)

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        """Modified to allow for requesting the session's current ``report``.

        The override specifies the kwarg ``id`` with a value "session" instead
        of the primary key.
        """
        if kwargs.get('id', None) != 'session':
            return super(ReportHandler, self).read(request, *args, **kwargs)
        return request.session.get('report')


class ReportResolverHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Report

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        "The interface for resolving a report, i.e. running a query."

        if not kwargs.has_key('id'):
            return rc.BAD_REQUEST

        format_type = request.GET.get('format', 'html')
        page_num = request.GET.get('page', None)
        per_page = request.GET.get('per_page', None)

        inst = request.session['report']

        if kwargs.get('id') != 'session':
            if int(kwargs['id']) != inst.id:
                try:
                    inst = self.queryset(request).get(pk=kwargs['id'])
                except ObjectDoesNotExist:
                    return rc.NOT_FOUND
                except MultipleObjectsReturned:
                    return rc.BAD_REQUEST

        user = request.user

        if not inst.has_permission(user):
            raise rc.FORBIDDEN

        # define the default context for use by ``get_queryset``
        # TODO can this be defined elsewhere? only scope depends on this, but
        # the user object has to propagate down from the view
        context = {'user': user}

        # fetch the report cache from the session, default to a new dict with
        # a few defaults. if a new dict is used, this implies that this a
        # report has not been resolved yet this session.
        cache = request.session.get(inst.REPORT_CACHE_KEY, {
            'offset': 0,
            'page_num': 1,
            'per_page': 10,
            'datakey': inst.get_datakey(request)
        })

        print 'before', cache

        # test if the cache is still valid, then attempt to fetch the requested
        # page from cache
        if inst.cache_is_valid(cache.get('timestamp', None)):
            # only update the cache if there are values specified for either arg
            if page_num:
                cache['page_num'] = int(page_num)
            if per_page:
                cache['per_page'] = int(per_page)

            rows = inst.get_page_from_cache(cache)

            # ``rows`` will only be None if no cache was found. attempt to
            # update the cache by running a partial query
            if rows is None:
                # since the cache is not invalid, the counts do not have to be run
                queryset = inst.get_queryset(run_counts=False, **context)
                cache['timestamp'] = datetime.now()

                rows = inst.update_cache(cache, queryset);

        # when the cache becomes invalid, the cache must be refreshed
        else:
            queryset, unique, count = inst.get_queryset(run_counts=True, **context)

            cache.update({
                'page_num': 1,
                'timestamp': datetime.now(),
                'offset': 0,
                'unique': unique,
                'count': count,
            })

            rows = inst.refresh_cache(cache, queryset)

        print 'after', cache

        request.session[inst.REPORT_CACHE_KEY] = cache

        paginator, page = inst.paginator_and_page(cache)

        return {
            'header': inst.perspective.header(),
            'unique': cache['unique'],
            'count': cache['count'],
            'pages': {
                'page': page.number,
                'pages': page.page_links(),
                'num_pages': paginator.num_pages,
            },
            'per_page': per_page,
            'rows': list(inst.perspective.format(rows, format_type)),
        }
