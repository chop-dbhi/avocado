import time
import logging

log = logging.getLogger(__name__)


class FieldCacheBase(object):
    def __init__(self, interface):
        self.interface = interface

        self.methods = []
        # Iterate over methods and determine the methods that have a cache
        # proxy defined.
        for key, value in self.interface.__dict__.iteritems():
            if callable(value) and hasattr(value, '__cacheproxy__'):
                self.methods.append(key)

    def clear(self, methods=None):
        pass

    def cache(self, methods=None):
        pass


class FieldCache(FieldCacheBase):
    def cache(self, methods=None):
        methods = methods or self.methods

        for method in methods:
            func = getattr(self.interface, method)

            if func.cached():
              log.debug('Data already cache', extra={
                  'field': unicode(self.interface),
                  'method': method,
              })
              continue

            t0 = time.time()
            func()
            t1 = time.time() - t0

            log.debug('Data cache set'.format(t1), extra={
                'field': unicode(self.interface),
                'method': method,
                'time': t1,
            })

    def clear(self, methods=None):
        methods = methods or self.methods

        for method in methods:
            func = getattr(self.interface, method)

            if not func.cached():
              log.debug('Data already cache', extra={
                  'field': unicode(self.interface),
                  'method': method,
              })
              continue

            t0 = time.time()
            func.clear()
            t1 = time.time() - t0

            log.debug('Data cache clear'.format(t1), extra={
                'field': unicode(self.interface),
                'method': method,
                'time': t1,
            })
