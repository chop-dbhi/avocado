def ins(value):
    """Simple test to distinguish sequences that are not strings.

    >>> ins(None)
    False
    >>> ins('')
    False
    >>> ins(u'')
    False
    >>> ins(r'')
    False
    >>> ins(True)
    False

    >>> ins([])
    True
    >>> ins(())
    True
    >>> ins({})
    True
    >>> ins(set([]))
    True
    """
    if not isinstance(value, basestring):
        try:
            iter(value)
            return True
        except TypeError:
            pass
    return False
