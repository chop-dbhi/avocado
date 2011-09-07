from avocado.store.models import Perspective
from .context import ContextForm, SessionContextForm

class PerspectiveForm(ContextForm):
    class Meta(ContextForm.Meta):
        model = Perspective


class SessionPerspectiveForm(SessionContextForm):
    class Meta(SessionContextForm.Meta):
        model = Perspective
