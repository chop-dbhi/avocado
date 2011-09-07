from avocado.store.models import Report
from .context import ContextForm, SessionContextForm

class ReportForm(ContextForm):
    "Simple form for validating metadata."
    def _save_for_proxy(self, session_obj, obj, explicit=True):
        self._save(obj, explicit=explicit)
        # proxy
        session_obj.proxy(obj)
        session_obj.scope.save(explicit=explicit)
        session_obj.perspective.save(explicit=explicit)
        session_obj.save()
        return obj

    def _save(self, obj, explicit):
        obj.scope.save(explicit=explicit)
        obj.perspective.save(explicit=explicit)
        obj.save()
        self.save_m2m()
        return obj

    class Meta(object):
        model = Report
        fields = ('name', 'description', 'keywords')


class SessionReportForm(SessionContextForm):
    class Meta(object):
        model = Report
        fields = ('name', 'description', 'keywords')
