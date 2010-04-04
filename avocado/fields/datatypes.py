"""
The Datatype class drives the validation flow for each requested field of the
query itself. The Datatype class is intended to be subclassed for actual use.
"""
import random
import decimal

from datetime import datetime
from django import forms
from avocado.exceptions import ValidationError
from .operators import *
from .fields import RangeField
from .widgets import DateRangeWidget

MAX_SAMPLE_SIZE = 80

def _reduce_sample_size(pts, size=MAX_SAMPLE_SIZE):
    sample = []
    if len(pts) > size:
        first, last = pts.pop(0), pts.pop(len(pts)-1)
        sample.append(first)
        for i in range(size-2):
            n = int(random.random() * len(pts))
            sample.append(pts[n])
        sample.append(last)
    else:
        sample = pts
    return sample

class BadOperator(Exception):
    pass


class Datatype(object):
    "Acts as an interface for subclassing."
    name = ''
    operators = ()

    def _validate_op(self, operator):
        for op in self.operators:
            if op.operator == operator:
                return op
        raise BadOperator, 'No operator %s exists for the %s datatype' % \
            (operator, self.name)

    def _validate_val(self, value):
        pass

    def sample(self, pts):
        "Returns a set of pts in which the x-value is converted to a string."
        sample = _reduce_sample_size(pts, 30)
        return map(lambda x: (str(x[0]), x[1]), sample), 'string'

    def op_choices(self):
        return tuple([(x.operator, x.display) for x in self.operators])

    def op_field(self):
        return forms.ChoiceField(choices=self.op_choices())

    def val_field(self):
        return forms.CharField()

    def validate(self, operator, value):
        return self._validate_op(operator), self._validate_val(value)


class String(Datatype):
    name = 'string'
    operators = (contains, does_not_contain, exactci, not_exactci)

    def _validate_val(self, val):
        "Expects a 1-item list."
        return u'%s' % val[0]


class StringList(Datatype):
    name = 'string-list'
    operators = (inlist, not_inlist)

    def _validate_val(self, val):
        "Expects a 1-item list containing new-line delimited string."
        return map(lambda x: u'%s' % x, val[0].strip().split('\n'))

    def val_field(self):
        return forms.CharField(widget=forms.Textarea(attrs={'rows': 8,
            'cols': 25}))


class Choice(Datatype):
    name = 'choice'
    operators = (inlist, not_inlist)

    def _validate_val(self, val):
        "Expects a list."
        return map(lambda x: u'%s' % x, val)

    def val_field(self):
        return forms.MultipleChoiceField(choices=(),
            help_text=u'Hold Ctrl on Windows or Cmd on Mac')


class Integer(Datatype):
    name = 'integer'
    operators = (between, not_between, less_than, greater_than,
        less_than_or_equal, greater_than_or_equal, exact, not_exact)

    def _validate_val(self, val):
        "Expects a list containing an integer string."
        val = filter(lambda x: x != '', val)
        if len(val) > 1:
            # for the between operator
            try:
                return sorted([int(x) for x in val])
            except ValueError:
                raise ValidationError
        try:
            return int(val[0])
        except ValueError:
            raise ValidationError

    def sample(self, pts):
        "Returns a set of sorted points."
        sample = _reduce_sample_size(pts)
        sample.sort(lambda x, y: cmp(x[0], y[0]))
        return sample, 'number'

    def op_field(self):
        return forms.ChoiceField(choices=self.op_choices(),
            widget=forms.Select(attrs={'class': 'range'}))

    def val_field(self):
        return RangeField()


class Decimal(Integer):
    name = 'decimal'

    def _validate_val(self, val):
        "Expects a list containing a numerical string."
        val = filter(lambda x: x != '', val)
        if len(val) > 1:
            try:
                return sorted([decimal.Decimal(x) for x in val])
            except ValueError:
                raise ValidationError, 'Bad decimal string %s' % str(val)
        try:
            return decimal.Decimal(val[0])
        except ValueError:
            raise ValidationError, 'Bad decimal string %s' % str(val[0])

    def sample(self, pts):
        "Returns a set of sorted points."
        sample = _reduce_sample_size(pts)
        sample.sort(lambda x, y: cmp(x[0], y[0]))
        sample = map(lambda x: (float(str(x[0])), x[1]), sample)
        return sample, 'number'


class Boolean(Datatype):
    name = 'boolean'
    operators = (exact,)

    allowed_values = (
        (True, u'Yes'),
        (False,  u'No'),
    )

    choices = (
        ('', u'----'),
        ('Yes', u'Yes'),
        ('No',  u'No'),
    )

    def _validate_val(self, val):
        "Expects a 1-item list containing a boolean string."
        if val[0].lower() in ('yes', 'true', '1'):
            return True
        return False

    def sample(self, pts):
        "Expects at the most two points representing True and False."
        return map(lambda x: (bool(x[0]), x[1]), pts), 'boolean'

    def op_field(self):
        return forms.CharField(widget=forms.HiddenInput(),
            initial=self.operators[0].operator)

    def val_field(self):
        return forms.ChoiceField(choices=self.choices)


class Date(Datatype):
    name = 'date'
    operators = (between, not_between, less_than, greater_than,
        less_than_or_equal, greater_than_or_equal, exact, not_exact)

    def _validate_val(self, val):
        "Expects a 1 or 2-item list containing a date string."
        # TODO make this date handling more robust
        if len(val) > 1:
            try:
                return sorted(map(lambda x: datetime.strptime(x,
                    '%m/%d/%Y').date(), val[:2]), cmp=lambda x,y: cmp(x, y))
            except ValueError:
                raise ValidationError, 'Bad date string %s' % str(val)
        try:
            return datetime.strptime(val[0], '%m/%d/%Y').date()
        except ValueError:
            raise ValidationError, 'Bad date string %s' % str(val)

    def op_field(self):
        return forms.ChoiceField(choices=self.op_choices(),
            widget=forms.Select(attrs={'class': 'range'}))

    def val_field(self):
        return RangeField(widget=DateRangeWidget,
            help_text=u'Format is MM/DD/YYYY')


datatypes = (String(), StringList(), Integer(), Decimal(), Boolean(), Date(),
    Choice())

def get(name):
    for x in datatypes:
        if getattr(x, 'name', '') == name:
            return x
    raise TypeError, 'no %s data type found' % name
