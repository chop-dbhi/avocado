"""
Simple set of classes that roughly map one-to-one to the operations that can
performed in the django ORM.

Each class must provide a `clean' method that validates a given `value' is of
the right length and in some cases, type.
"""

__all__ = ('exact', 'iexact', 'contains', 'inlist', 'lt', 'gt', 'lte', 'gte',
    'between', 'null', 'notbetween', 'notexact', 'notiexact', 'doesnotcontain',
    'notinlist', 'notnull', 'ValidationError')


class ValidationError(Exception):
    pass


class Operator(object):
    negated = False
    operator = ''
    display = ''

    def __str__(self):
        if self.negated:
            return '%s (~%s)' % (self.display, self.operator)
        return '%s (%s)' % (self.display, self.operator)   

    def __unicode__(self):
        if self.negated:
            return u'%s (~%s)' % (self.display, self.operator)
        return u'%s (%s)' % (self.display, self.operator)

    def __repr__(self):
        return str(self.__class__)

    def clean(self, value):
        "Cleans and verifies `value' can be used for this operator."
        if type(value) in (list, tuple):
            if len(value) > 0:
                return value[0]
            return ''
        return value

class Exact(Operator):
    operator = 'exact'
    display = '='
exact = Exact()


class iExact(Operator):
    operator = 'iexact'
    display = '='
iexact = iExact()


class Contains(Operator):
    operator = 'icontains'
    display = 'contains'
contains = Contains()


class InList(Operator):
    operator = 'in'
    display = 'in list'

    def clean(self, value):
        if type(value) not in (list, tuple):
            value = value.split('\n')
        return value
inlist = InList()


class LessThan(Operator):
    operator = 'lt'
    display = '<'
lt = LessThan()


class GreaterThan(Operator):
    operator = 'gt'
    display = '>'
gt = GreaterThan()


class LessThanOrEqual(Operator):
    operator = 'lte'
    display = '<='
lte = LessThanOrEqual()


class GreaterThanOrEqual(Operator):
    operator = 'gte'
    display = '>='
gte = GreaterThanOrEqual()


class Between(Operator):
    operator = 'range'
    display = 'between'

    def clean(self, value):
        if not type(value) in (list, tuple):
            raise ValidationError, 'the value must be a list'
        if len(value) != 2:
            raise ValidationError, '"between" requires a list of two values'
        return value
between = Between()


class Null(Operator):
    operator = 'isnull'
    display = 'is null'
null = Null()


class NotBetween(Between):
    negated = True
    display = 'not between'
notbetween = NotBetween()


class NotExact(Exact):
    negated = True
    display = 'not ='
notexact = NotExact()


class NotiExact(iExact):
    negated = True
    display = 'not ='
notiexact = NotiExact()


class DoesNotContain(Contains):
    negated = True
    display = 'does not contain'
doesnotcontain = DoesNotContain()


class NotInList(InList):
    negated = True
    display = 'not in list'
notinlist = NotInList()


class NotNull(Null):
    negated = True
    display = 'not null'
notnull = NotNull()