from warnings import warn
from avocado.core import loader


class BaseOperatorMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        new_cls.uid = ('-' if new_cls.negated else '') + new_cls.lookup
        return new_cls


class BaseOperator(object):
    __metaclass__ = BaseOperatorMetaclass

    lookup = ''
    short_name = ''
    verbose_name = ''
    negated = False

    def __str__(self):
        return '%s (%s)' % (self.verbose_name, self.uid)

    def __unicode__(self):
        return u'%s' % str(self)

    def __repr__(self):
        return u'<Operator: "%s" (%s)>' % (self.verbose_name, self.uid)

    @property
    def operator(self):
        warn('self.operator is deprecated, use self.lookup instead',
            DeprecationWarning)
        return self.lookup

    def coerce_to_unicode(self, value):
        return unicode(value)

    def is_valid(self, value):
        raise NotImplemented('Use an Operator subclass')

    def text(self, value):
        raise NotImplemented('Use an Operator subclass')


class SimpleTypeOperator(BaseOperator):
    "Operator class for non-container type values. Includes strings."
    def is_valid(self, value):
        return not hasattr(value, '__iter__')

    def text(self, value):
        value = self.coerce_to_unicode(value)
        return u'%s %s' % (self.verbose_name, value)


class StringOperator(SimpleTypeOperator):
    "Operator class for string-only lookups."
    def is_valid(self, value):
        return isinstance(value, basestring)


class ContainerTypeOperator(BaseOperator):
    "Operator class for container type values. Excludes strings."
    join_string = 'and'
    max_list_size = 3

    def is_valid(self, value):
        return hasattr(value, '__iter__')

    def text(self, value):
        value = map(self.coerce_to_unicode, value)

        last = value[-1]
        length = len(value) - 1

        if length == 0:
            return u'%s %s' % (self.verbose_name, last)

        if length > self.max_list_size:
            head = value[:self.max_list_size]
        else:
            head = value[:-1]
        text = self.verbose_name + ' ' + ', '.join(head)

        # Add the leftover item count for the tail of the list
        tail = length - self.max_list_size
        if tail > 0:
            text += ' ... (%s more)' % tail

        return text + (' %s ' % self.join_string) + last


class Null(BaseOperator):
    lookup = 'isnull'
    short_name = 'is null'
    verbose_name = 'is null'

    def is_valid(self, value):
        return isinstance(value, bool)

    def text(self, value):
        "Do not return value"
        return unicode(self.verbose_name if value else NotNull.verbose_name)


class NotNull(Null):
    short_name = 'not null'
    verbose_name = 'is not null'
    negated = True

    def text(self, value):
        "Do not return value"
        return unicode(self.verbose_name if value else Null.verbose_name)


class Exact(SimpleTypeOperator):
    lookup = 'exact'
    short_name = '='
    verbose_name = 'is equal to'

    def text(self, value):
        if isinstance(value, bool):
            return u'is {}'.format(value)
        return super(Exact, self).text(value)


class NotExact(Exact):
    short_name = '!='
    verbose_name = 'is not equal to'
    negated = True

    def text(self, value):
        # Easier to read 'is False', rather than 'is not True'
        if isinstance(value, bool):
            return u'is {}'.format(not value)
        return super(NotExact, self).text(value)


# String-specific lookups
class InsensitiveExact(StringOperator):
    lookup = 'iexact'
    short_name = '='
    verbose_name = 'is equal to'


class InsensitiveNotExact(InsensitiveExact):
    short_name = '!='
    verbose_name = 'is not equal to'
    negated = True


class Contains(StringOperator):
    lookup = 'contains'
    short_name = 'contains'
    verbose_name = 'contains the text'


class InsensitiveContains(Contains):
    lookup = 'icontains'
    short_name = 'contains'
    verbose_name = 'contains the text'


class NotContains(Contains):
    short_name = 'does not contain'
    verbose_name = 'does not contain'
    negated = True


class NotInsensitiveContains(InsensitiveContains):
    short_name = 'does not contain'
    verbose_name = 'does not contain'
    negated = True


# Numerical and lexicographical lookups
class LessThan(SimpleTypeOperator):
    lookup = 'lt'
    short_name = '<'
    verbose_name = 'is less than'


class GreaterThan(SimpleTypeOperator):
    lookup = 'gt'
    short_name = '>'
    verbose_name = 'is greater than'


class LessThanOrEqual(SimpleTypeOperator):
    lookup = 'lte'
    short_name = '<='
    verbose_name = 'is less than or equal to'


class GreaterThanOrEqual(SimpleTypeOperator):
    lookup = 'gte'
    short_name = '>='
    verbose_name = 'is greater than or equal to'


# Operators for container types (excluding strings)
class InList(ContainerTypeOperator):
    lookup = 'in'
    short_name = 'includes'
    verbose_name = 'includes'


class NotInList(InList):
    short_name = 'excludes'
    verbose_name = 'excludes'
    negated = True


class Range(ContainerTypeOperator):
    join_string = 'and'
    lookup = 'range'
    short_name = 'between'
    verbose_name = 'is between'

    def is_valid(self, value):
        return super(Range, self).is_valid(value) and len(value) == 2

    def text(self, value):
        value = map(self.coerce_to_unicode, value)
        return '%s %s' % (self.verbose_name,
            ' and '.join(value))


class NotRange(Range):
    short_name = 'not between'
    verbose_name = 'is not between'
    negated = True


# Register operators
registry = loader.Registry()

# General equality
registry.register(Exact, Exact.uid)
registry.register(NotExact, NotExact.uid)

# String operators
registry.register(InsensitiveExact, InsensitiveExact.uid)
registry.register(Contains, Contains.uid)
registry.register(InsensitiveContains, InsensitiveContains.uid)
registry.register(InsensitiveNotExact, InsensitiveNotExact.uid)
registry.register(NotContains, NotContains.uid)
registry.register(NotInsensitiveContains, NotInsensitiveContains.uid)

# Null
registry.register(Null, Null.uid)
registry.register(NotNull, NotNull.uid)

# Numerical or lexicographical comparison
registry.register(LessThan, LessThan.uid)
registry.register(GreaterThan, GreaterThan.uid)
registry.register(LessThanOrEqual, LessThanOrEqual.uid)
registry.register(GreaterThanOrEqual, GreaterThanOrEqual.uid)

# List
registry.register(InList, InList.uid)
registry.register(NotInList, NotInList.uid)

# Range
registry.register(Range, Range.uid)
registry.register(NotRange, NotRange.uid)

loader.autodiscover('operators')
