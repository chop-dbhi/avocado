import re

class CamelCaser(object):

    UNDERSCORE = re.compile(r'([^\A_])_+([^_])')

    def _upper(self, m):
        f, l = m.groups()
        return '%s%s' % (f, l.upper())

    def camel(self, s):
        return self.UNDERSCORE.sub(self._upper, s)

    def camel_keys(self, rdict, cdict=None):
        cdict = cdict or {}
        for k, v in rdict.items():
            ck = self.camel(k)
            if type(v) is dict:
                cdict[ck] = self.camel_keys(v)
            else:
                cdict[ck] = v
        return cdict

camelcaser = CamelCaser()