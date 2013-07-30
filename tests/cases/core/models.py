from django.db import models
from avocado.core.cache import cached_method
from avocado.core.cache.model import CacheManager

class Foo(models.Model):
    objects = CacheManager()

    def get_version(self, label=None):
        return 1

    @cached_method(timeout=2)
    def unversioned(self):
        return [1]

    @cached_method(version='get_version', timeout=2)
    def versioned(self):
        return [2]

    @cached_method(version=get_version, timeout=2)
    def callable_versioned(self):
        return [3]
