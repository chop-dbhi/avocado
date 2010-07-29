from avocado.modeltree import DEFAULT_MODELTREE

class ConceptSet(object):
    """A ConceptSet provides a simple interface that implements Concept-like
    model objects.

        `queryset' - a Concept-subclass queryset that acts as a starting point
        for retrieving objects from
        
        `modeltree' - a ModelTree instance that should have a root model that
        is the same as the queryset(s) being processed via the public methods
    """
    def __init__(self, queryset, modeltree=DEFAULT_MODELTREE):
        self.queryset = queryset
        self.modeltree = modeltree

    def __getstate__(self):
        state = self.__dict__.copy()
        state['query'] = state.pop('queryset').query
        return state
    
    def __setstate__(self, state, queryset=None):
        if queryset is None:
            raise NotImplemented, '__setstate__ must be implemented in a subclass'
        queryset.query = state.pop('query')
        state['queryset'] = queryset
        self.__dict__.update(state)