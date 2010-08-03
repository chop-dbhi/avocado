"""
Set of classes that provide a means of generating, validating and cleaning
two form fields that define the `operator' and `value' defined by the user.

In most cases, only certain operators make sense to be utilized by certain
FieldType subclasses, but this method provides a means to be more restrictive
on what operators are allowed.
"""

from django import forms
from django.core.exceptions import ValidationError

from avocado.fields.operators import *

__all__ = ('IntegerField', 'DecimalField', 'FloatField', 'DateField',
    'TimeField', 'DateTimeField', 'BooleanField', 'NullBooleanField',
    'ChoiceField', 'ModelChoiceField', 'MultipleChoiceField',
    'ModelMultipleChoiceField', 'ListField')

class OperatorNotPermitted(Exception):
    pass


class FieldType(object):
    formfield = forms.CharField
    widget = None
    operators = None


class NumberType(FieldType):
    operators = (exact, notexact, lt, lte, gt, gte, between, notbetween, null,
        notnull)


class CharField(FieldType):
    operators = (iexact, notiexact, contains, doesnotcontain,
        inlist, notinlist, null, notnull)


class IntegerField(NumberType):
    formfield = forms.IntegerField


class DecimalField(NumberType):
    formfield = forms.DecimalField


class FloatField(NumberType):
    formfield = forms.FloatField


class DateField(NumberType):
    formfield = forms.DateField


class TimeField(NumberType):
    formfield = forms.TimeField


class DateTimeField(NumberType):
    formfield = forms.DateTimeField


class BooleanField(FieldType):
    formfield = forms.BooleanField
    operators = (exact,)


class NullBooleanField(FieldType):
    formfield = forms.BooleanField
    operators = (exact, null, notnull)


class ChoiceField(FieldType):
    formfield = forms.ChoiceField
    operators = (exact, notexact, null, notnull)


class ModelChoiceField(ChoiceField):
    formfield = forms.ModelChoiceField


class MultipleChoiceField(FieldType):
    formfield = forms.MultipleChoiceField
    operators = (inlist, notinlist)


class ModelMultipleChoiceField(MultipleChoiceField):
    formfield = forms.ModelMultipleChoiceField


class ListField(FieldType):
    widget = forms.Textarea
    operators = (inlist, notinlist)


MODEL_FIELD_MAP = {
    'AutoField': IntegerField,
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
