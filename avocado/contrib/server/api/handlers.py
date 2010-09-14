from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from piston.handler import BaseHandler
from piston.utils import rc

from avocado.models import Category, Scope, Perspective, Report
from avocado.contrib.server.api.models import CriterionProxy

class CategoryHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Category
    fields = ('id', 'name', 'icon')


class CriterionHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = CriterionProxy

    def queryset(self, request):
        "Overriden to allow for user specificity."
        # restrict_by_group only in effect when FIELD_GROUP_PERMISSIONS is
        # enabled
        if hasattr(self.model.objects, 'restrict_by_group'):
            groups = request.user.groups.all()
            return self.model.objects.restrict_by_group(groups)
        return self.model.objects.all()

    def read(self, request, *args, **kwargs):
        obj = super(CriterionHandler, self).read(request, *args, **kwargs)
        # if an instance was returned, simply return the view responses
        if isinstance(obj, self.model):
            return obj.view_responses()

        # apply fulltext if the 'q' GET param exists
        if request.GET.has_key('q'):
            obj = self.model.objects.fulltext_search(request.GET.get('q'), obj, True)
        return map(lambda x: x.json(), obj)


class ScopeHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    model = Scope
    fields = ('id', 'name', 'description', 'keywords', 'definition', 'store')

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        """Modified to allow for requesting the session's current ``scope``.
        
        The override specifies the kwarg ``id`` with a value "session" instead
        of the primary key.
        """
        if kwargs.get('id', None) != 'session':
            return super(ScopeHandler, self).read(request, *args, **kwargs)
        return request.session.get('report').scope

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
        
        # assume the PUT request is only the store
        if kwargs['id'] == 'session':
            inst.write(request.PUT)

        # an object has been targeted via the ``id`` referenced in the url
        else:
            if kwargs['id'] != inst.id:
                try:
                    inst = self.queryset(request).get(pk=kwargs['id'])
                except ObjectDoesNotExist:
                    return rc.NOT_FOUND
                except MultipleObjectsReturned:
                    return rc.BAD_REQUEST

            data = request.PUT.copy()

            store = data.pop('store', None)
            attrs = self.flatten_dict(data)

            # special case
            if store is not None:
                inst.write(store)

            for k, v in attrs.iteritems():
                setattr(inst, k, v)

            inst.save()

        request.session['report'].scope = inst
        request.session.modified = True
        
        return rc.ALL_OK


class PerspectiveHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    model = Perspective
    fields = ('id', 'name', 'description', 'keywords', 'definition', 'store')

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
        inst = request.session['report'].perspective
        
        # assume the PUT request is only the store
        if kwargs['id'] == 'session':
            inst.write(request.PUT)

        # an object has been targeted via the ``id`` referenced in the url
        else:
            if kwargs['id'] != inst.id:
                try:
                    inst = self.queryset(request).get(pk=kwargs['id'])
                except ObjectDoesNotExist:
                    return rc.NOT_FOUND
                except MultipleObjectsReturned:
                    return rc.BAD_REQUEST

            data = request.PUT.copy()

            store = data.pop('store', None)
            attrs = self.flatten_dict(data)

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
    fields = ('id', 'name',
        ('scope', ScopeHandler.fields),
        ('perspective', PerspectiveHandler.fields)
    )

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
