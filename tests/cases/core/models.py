from django.db import models
from avocado.core.cache import cached_method, CacheManager


class Foo(models.Model):
    objects = CacheManager()

    value = models.IntegerField(default=4)

    def get_version(self, label=None):
        return 1

    @cached_method(timeout=1)
    def unversioned(self):
        return [1]

    @cached_method(version='get_version', timeout=1)
    def versioned(self):
        return [2]

    @cached_method(version=get_version, timeout=1)
    def callable_versioned(self):
        return [3]

    @cached_method
    def default_versioned(self):
        return [self.value]
