from piston.handler import BaseHandler
from avocado.models import Category

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
        return self.models.objects.all()

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
