"""
Set of classes that provide a means of generating, validating and cleaning
two form fields that define the `operator' and `value' defined by the user.

In most cases, only certain operators make sense to be utilized by certain
FieldType subclasses, but this method provides a means to be more restrictive
on what operators are allowed.
"""

from django import forms
from avocado.fields.operators import *

MODEL_FIELD_MAP = {
    'CharField': CharField,
    'IntegerField': IntegerField,
    'FloatField': FloatField,
    'DecimalField': DecimalField,
    'DateField': DateField,
    'DateTimeField': DateTimeField,
    'TimeField': TimeField,
    'BooleanField': BooleanField,
    'NullBooleanField': NullBooleanField,
    'ForeignKey': ModelChoiceField,
}

def _operator_dict(*args):
    return dict(map(lambda x: (x.operator, x), args))

class OperatorNotPermitted(Exception):
    pass


class FieldType(object):
    field = forms.CharField
    widget = None
    operators = _operator_dict()
    
    def __init__(self):
        if not self.operators:
            raise NotImplementedError, 'subclasses must have at least one ' \
                'operator associated with it'

    def _get_operator(self, operator):
        try:
            return self.operators[operator]
        except KeyError:
            raise OperatorNotPermitted, '%s is not permitted for field type %s' % \
                (operator, self.__class__.__name__)
    
    def clean(self, operator, value):
        return self._get_operator(operator).clean(value)


class CharField(FieldType):
    operators = _operator_dict(iexact, notiexact, contains, doesnotcontain,
        null, notnull)


class IntegerField(FieldType):
    field = forms.IntegerField
    operators = _operator_dict(exact, notexact, lt, lte, gt, gte, between,
        notbetween, null, notnull)


class DecimalField(IntegerField):
    field = forms.DecimalField


class FloatField(IntegerField):
    field = forms.FloatField


class DateField(IntegerField):
    field = forms.DateField


class TimeField(IntegerField):
    field = forms.TimeField
    

class DateTimeField(IntegerField):
    field = forms.DateTimeField


class BooleanField(FieldType):
    field = forms.BooleanField
    operators = _operator_dict(exact)


class NullBooleanField(FieldType):
    field = forms.NullBooleanField
    operators = _operator_dict(exact, null, notnull)


class ChoiceField(FieldType):
    field = forms.ChoiceField
    operators = _operator_dict(exact, notexact, null, notnull)


class ModelChoiceField(ChoiceField):
    field = forms.ModelChoiceField


class MultipleChoiceField(FieldType):
    field = forms.MultipleChoiceField
    operators = _operator_dict(inlist, notinlist)


class ModelMultipleChoiceField(MultipleChoiceField):
    field = forms.ModelMultipleChoiceField


class ListField(FieldType):
    widget = forms.Textarea
    operators = _operator_dict(inlist, notinlist)