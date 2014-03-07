try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


REPR_OUTPUT_SIZE = 20


class ChoicesDict(OrderedDict):
    "OrdereDict that yields the key and value on iteration."
    def __iter__(self):
        iterator = super(ChoicesDict, self).__iter__()

        for key in iterator:
            yield key, self[key]

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE + 1])

        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = '...(remaining elements truncated)...'

        return repr(tuple(data))
