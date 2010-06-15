def is_iter_not_string(value):
    """Simple test to distinguish sequences that are not strings.

    >>> is_iter_not_string(None)
    False
    >>> is_iter_not_string('')
    False
    >>> is_iter_not_string(u'')
    False
    >>> is_iter_not_string(r'')
    False
    >>> is_iter_not_string(True)
    False

    >>> is_iter_not_string([])
    True
    >>> is_iter_not_string(())
    True
    >>> is_iter_not_string({})
    True
    >>> is_iter_not_string(set([]))
    True
    """
    if not isinstance(value, basestring):
        try:
            iter(value)
            return True
        except TypeError:
            pass
    return False
