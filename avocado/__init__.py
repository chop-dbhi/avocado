VERSION = (0, 9, 0, 'beta', 1)

def get_version():
    version = '%s.%s.%s' % VERSION[:3]

    if len(VERSION) > 3:
        if version[3:] == ('alpha', 0):
            version = '%s pre-alpha' % version
        else:
            if VERSION[3] != 'final':
                version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version
