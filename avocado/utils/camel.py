import re

class CamelCaser(object):
    UNDERSCORE = re.compile(r'([^\A_])_+([^_])')

    def __call__(self, s):
        return self.camel(s)

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


class UnCamelCaser(object):
    def __call__(self, s):
        return self.uncamel(s)

    def uncamel(self, s):
        toks = [s[0]]
        for x in s[1:]:
            if x.isupper():
                toks.append(' ')
            toks.append(x)
        return ''.join(toks)


camel= CamelCaser()
uncamel = UnCamelCaser()
