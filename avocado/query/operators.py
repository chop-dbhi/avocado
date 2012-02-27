"""
Simple set of classes that roughly map one-to-one to the operations that can
performed in the django ORM.

Each class must provide a `clean' method that checks a given `value' is of
the right length and in some cases, type.
"""

class Operator(object):
    operator = ''
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
    def uid(self):
        if self.negated:
            return '-%s' % self.operator
        return '%s' % self.operator

    def stringify(self, value):
        s = '<b>%s</b>'
        if value is None:
            if self.negated:
                value = 'has any value'
            else:
                value = 'has no value'
        elif type(value) is bool:
            value = 'Yes' if value else 'No'
        else:
            value = str(value)

        return s % value

    def check(self, value):
        pass

    def text(self, value):
        pass


class PrimitiveOperator(Operator):
    def check(self, value):
        if hasattr(value, '__iter__'):
            return False
        return True

    def text(self, value):
        value = self.stringify(value)
        return '%s %s' % (self.verbose_name, value)

class Exact(PrimitiveOperator):
    operator = 'exact'
    short_name = '='
    verbose_name = 'is equal to'

exact = Exact()


class iExact(PrimitiveOperator):
    operator = 'iexact'
    short_name = '='
    verbose_name = 'is equal to'

iexact = iExact()


class Contains(PrimitiveOperator):
    operator = 'contains'
    short_name = 'contains'
    verbose_name = 'contains the text'

contains = Contains()


class iContains(PrimitiveOperator):
    operator = 'icontains'
    short_name = 'contains'
    verbose_name = 'contains the text'

icontains = iContains()


class LessThan(PrimitiveOperator):
    operator = 'lt'
    short_name = '<'
    verbose_name = 'is less than'

lt = LessThan()


class GreaterThan(PrimitiveOperator):
    operator = 'gt'
    short_name = '>'
    verbose_name = 'is greater than'

gt = GreaterThan()


class LessThanOrEqual(PrimitiveOperator):
    operator = 'lte'
    short_name = '<='
    verbose_name = 'is less than or equal to'

lte = LessThanOrEqual()


class GreaterThanOrEqual(PrimitiveOperator):
    operator = 'gte'
    short_name = '>='
    verbose_name = 'is greater than or equal to'

gte = GreaterThanOrEqual()


class Null(PrimitiveOperator):
    operator = 'isnull'
    short_name = 'is null'
    verbose_name = 'is null'

    def text(self, value):
        "Do not return operator"
        return self.stringify(None)

null = Null()

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


class DoesNotiContain(iContains):
    short_name = 'does not contain'
    verbose_name = 'does not contain'
    negated = True

doesnoticontain = DoesNotiContain()


class NotNull(Null):
    short_name = 'not null'
    verbose_name = 'is not null'
    negated = True

notnull = NotNull()

# operators that support or require a sequence of values

class SequenceOperator(Operator):
    def check(self, value):
        if ins(value):
            return True
        return False

    def text(self, value):
        value = map(self.stringify, value)
        if len(value) == 1:
            return '%s %s' % (Exact.verbose_name, value[0])
        return '%s %s' % (self.verbose_name, ' or '.join(value))


class InList(SequenceOperator):
    operator = 'in'
    short_name = 'in list'
    verbose_name = 'is either'

    def text(self, value):
        value = map(self.stringify, value)
        if len(value) == 1:
            return '%s %s' % (Exact.verbose_name, value[0])
        value = ', '.join(value[:-1]) + ' or %s' % value[-1]
        return '%s %s' % (self.verbose_name, value)

inlist = InList()


class Between(SequenceOperator):
    operator = 'range'
    short_name = 'between'
    verbose_name = 'is between'

    def check(self, value):
        if super(Between, self).check(value) and len(value) == 2:
            return True
        return False

    def text(self, value):
        value = map(self.stringify, value)
        return '%s %s' % (self.verbose_name,
            ' and '.join(value))

between = Between()


class NotBetween(Between):
    short_name = 'not between'
    verbose_name = 'is not between'
    negated = True

notbetween = NotBetween()


class NotInList(InList):
    short_name = 'not in list'
    verbose_name = 'is not'
    negated = True

notinlist = NotInList()


OPERATORS = (exact, notexact, iexact, notiexact, contains, doesnotcontain,
    icontains, doesnoticontain, gt, lt, gte, lte, null, notnull, inlist,
    notinlist, between, notbetween)

OPERATOR_DICT = dict((x.uid, x) for x in OPERATORS)

def get(uid):
    return OPERATOR_DICT.get(uid, None)
