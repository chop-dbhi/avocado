class ConceptSet(object):
    """A ConceptSet provides a simple interface that implements Concept-like
    model objects.

        `queryset' - a Concept-subclass queryset that acts as a starting point
        for retrieving objects from
        
        `modeltree' - a ModelTree instance that should have a root model that
        is the same as the queryset(s) being processed via the public methods
    """
    def __init__(self, queryset, model_tree):
        self.queryset = queryset
        self.model_tree = model_tree

    def __getstate__(self):
        dict_ = self.__dict__.copy()
        dict_['query'] = dict_.pop('queryset').query
        return dict_
    
    def __setstate__(self, dict_, queryset=None):
        if queryset is None:
            raise NotImplemented, '__setstate__ must be implemented in a subclass'
        queryset.query = dict_.pop('query')
        dict_['queryset'] = queryset
        self.__dict__.update(dict_)