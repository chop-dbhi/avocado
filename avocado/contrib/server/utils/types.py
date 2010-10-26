def uni2str(data):
    "Recursively iterates over a data structure and converts unicode to str"
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, dict):
        return dict(map(uni2str, data.iteritems()))
    elif isinstance(data, (list, tuple, set, frozenset)):
        return type(data)(map(uni2str, data))
    else:
        return data


