from avocado.core import loader


class QueryView(object):
    """Provides a mean of defining/deriving additional metadata from a
    DataConcept and/or it's associated DataField for use downstream by a
    client application. A _default_ QueryView reference can defined for
    `DataConcept` via it's `queryview` field.

    To implement, override the `process` method and return a `dict` that can
    be serialized downstream.

    Additional context _may_ be supplied (but not guaranteed to be supplied)
    via the `context` dict such as the `request` object while be processed
    during an HTTP request/response cycle.

    `QueryView`s are not client specific. It is assumed that clients can make
    use of as little or as much metadata as they choose. That being said, if
    multiple clients are being used, it may be important to namespace the
    relevant metadata so to not cause key collisions.
    """
    def __call__(self, concept, **context):
        return self.process(concept, **context)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def process(self, concept, **context):
        return {}


registry = loader.Registry(default=QueryView)
loader.autodiscover('queryviews')