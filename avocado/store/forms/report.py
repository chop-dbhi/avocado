from avocado.store.models import Report
from .context import ContextForm, SessionContextForm

class ReportForm(ContextForm):
    class Meta(ContextForm.Meta):
        model = Report


class SessionReportForm(SessionContextForm):
    class Meta(object):
        model = Report
        fields = ('name', 'description', 'keywords')
