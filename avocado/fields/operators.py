"""
Simple set of classes that roughly map one-to-one to the operations that can
performed in the django ORM.

Each class must provide a `clean' method that validates a given `value' is of
the right length and in some cases, type.
"""

from django.core.exceptions import ValidationError

from avocado.utils.iter import is_iter_not_string

__all__ = ('exact', 'iexact', 'contains', 'inlist', 'lt', 'gt', 'lte', 'gte',
    'between', 'null', 'notbetween', 'notexact', 'notiexact', 'doesnotcontain',
    'notinlist', 'notnull')


class Operator(object):
    short_name = ''
    verbose_name = ''
    operator = ''
    negated = False

    def __str__(self):
        if self.negated:
            return '%s (~%s)' % (self.short_name, self.operator)
        return '%s (%s)' % (self.short_name, self.operator)   

    def __unicode__(self):
        if self.negated:
            return u'%s (~%s)' % (self.short_name, self.operator)
        return u'%s (%s)' % (self.short_name, self.operator)

    def __repr__(self):
        return str(self.__class__)

    def validate(self, value):
        "Cleans and verifies `value' can be used for this operator."
        raise NotImplementedError


class PrimitiveOperator(Operator):
    def validate(self, value):
        if is_iter_not_string(value):
            raise ValidationError, 'Expected a string or non-sequence type, instead got %r' % value


class SequenceOperator(Operator):
    def validate(self, value):
        if not is_iter_not_string(value):
            raise ValidationError, 'Expected a non-string sequence type, instead got %r' % value


class iExact(PrimitiveOperator):
    short_name = '='
    verbose_name = 'is equal to'
    operator = 'iexact'
iexact = iExact()


class Contains(PrimitiveOperator):
    short_name = 'contains'
    verbose_name = 'contains'
    operator = 'icontains'
contains = Contains()


class LessThan(PrimitiveOperator):
    short_name = '<'
    verbose_name = 'is less than'
    operator = 'lt'
lt = LessThan()


class GreaterThan(PrimitiveOperator):
    short_name = '>'
    verbose_name = 'is greater than'
    operator = 'gt'
gt = GreaterThan()


class LessThanOrEqual(PrimitiveOperator):
    short_name = '<='
    verbose_name = 'is less than or equal to'
    operator = 'lte'
lte = LessThanOrEqual()


class GreaterThanOrEqual(PrimitiveOperator):
    short_name = '>='
    verbose_name = 'is greater than or equal to'
    operator = 'gte'
gte = GreaterThanOrEqual()


class Null(PrimitiveOperator):
    short_name = 'is null'
    verbose_name = 'is null'
    operator = 'isnull'
null = Null()


class Exact(PrimitiveOperator):
    "Only used with boolean fields. Use `iexact' otherwise."
    short_name = '='
    verbose_name = 'is equal to'
    operator = 'exact'
exact = Exact()


class InList(SequenceOperator):
    short_name = 'in list'
    verbose_name = 'is in list'
    operator = 'in'
inlist = InList()


class Between(SequenceOperator):
    short_name = 'between'
    verbose_name = 'is between'
    operator = 'range'

    def validate(self, value):
        super(Between, self).validate(value)        
        if len(value) != 2:
            raise ValidationError, 'Two values expected'
between = Between()


class NotBetween(Between):
    short_name = 'not between'
    verbose_name = 'is not between'
    negated = True
notbetween = NotBetween()


class NotExact(Exact):
    short_name = '!='
    verbose_name = 'is not equal to'
    negated = True
notexact = NotExact()


class NotiExact(iExact):
    short_name = '!='
    verbose_name = 'is not equal to'
    negated = True
notiexact = NotiExact()


class DoesNotContain(Contains):
    short_name = 'does not contain'
    verbose_name = 'does not contain'
    negated = True
doesnotcontain = DoesNotContain()


class NotInList(InList):
    short_name = 'not in list'
    verbose_name = 'is not in list'
    negated = True
notinlist = NotInList()


class NotNull(Null):
    short_name = 'not null'
    verbose_name = 'is not null'
    negated = True
notnull = NotNull()
