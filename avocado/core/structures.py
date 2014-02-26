try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class ChoicesDict(OrderedDict):
    "OrdereDict that yields the key and value on iteration."
    def __iter__(self):
        iterator = super(ChoicesDict, self).__iter__()

        for key in iterator:
            yield key, self[key]
