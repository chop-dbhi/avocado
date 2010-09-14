from piston.handler import BaseHandler

from avocado.models import Category, Scope, Perspective, Report
from avocado.contrib.server.api.models import CriterionProxy

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



class CategoryHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Category
    fields = ('id', 'name', 'icon')


class ScopeHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Scope
    fields = ('id', 'store')

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        if kwargs.get('id', None) != 'session':
            return super(ScopeHandler, self).read(request, *args, **kwargs)
        return request.session.get('report').scope


class PerspectiveHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Perspective
    fields = ('id', 'store')    

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        if kwargs.get('id', None) != 'session':
            return super(PerspectiveHandler, self).read(request, *args, **kwargs)
        return request.session.get('report').perspective


class ReportHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Report
    fields = ('id', 'name',
        ('scope', ('id', 'store')),
        ('perspective', ('id', 'store'))
    )

    def queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def read(self, request, *args, **kwargs):
        if kwargs.get('id', None) != 'session':
            return super(ReportHandler, self).read(request, *args, **kwargs)
        return request.session.get('report')
