from avocado.store.models import Scope
from .context import ContextForm, SessionContextForm

class ScopeForm(ContextForm):
    class Meta(ContextForm.Meta):
        model = Scope


class SessionScopeForm(SessionContextForm):
    class Meta(SessionContextForm.Meta):
        model = Scope
