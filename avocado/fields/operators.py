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

    def clean(self, value):
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
notbetween = NotBetween()

class NotExact(Exact):
    negated = True
notexact = NotExact()

class NotiExact(iExact):
    negated = True
notiexact = NotiExact()

class DoesNotContain(Contains):
    negated = True
doesnotcontain = DoesNotContain()

class NotInList(Operator):
    negated = True
notinlist = NotInList()

class NotNull(Null):
    negated = True
notnull = NotNull()