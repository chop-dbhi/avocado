# {{{ http://code.activestate.com/recipes/576563/ (r1)
def cached_property(f):
    "Returns a cached property that is calculated by function ``f``"
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x
        
    return property(get)
