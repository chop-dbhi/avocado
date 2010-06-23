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
    field_class = forms.CharField
    widget_class = None
    operators = ()

    def __init__(self):
        if not self.operators:
            raise NotImplementedError, 'subclasses must have at least one ' \
                'operator associated with it'
        self._operators = dict(map(lambda x: (x.operator, x), self.operators))

    def _get_operator(self, operator):
        try:
            return self._operators[operator]
        except KeyError:
            raise OperatorNotPermitted, '%s is not permitted for field type %s' % \
                (operator, self.__class__.__name__)

    def clean(self, operator, value):
        """Validation is a multi-step process including:
            - validating the operator is allowed for this field type
            - cleaning the value based on the form field
            - testing whether the value is appropriate for the operator
        """
        formfield = self.field_class()

        try:
            clean_value = formfield.clean(value)
        except forms.ValidationError:
            pass

        if self._get_operator(operator).is_valid(clean_value):
            return clean_value
        raise ValidationError, ''


class NumberType(FieldType):
    operators = (exact, notexact, lt, lte, gt, gte, between, notbetween, null,
        notnull)


class CharField(FieldType):
    operators = (iexact, notiexact, contains, doesnotcontain, null, notnull)


class IntegerField(NumberType):
    field_class = forms.IntegerField


class DecimalField(NumberType):
    field_class = forms.DecimalField


class FloatField(NumberType):
    field_class = forms.FloatField


class DateField(NumberType):
    field_class = forms.DateField


class TimeField(NumberType):
    field_class = forms.TimeField


class DateTimeField(NumberType):
    field_class = forms.DateTimeField


class BooleanField(FieldType):
    field_class = forms.BooleanField
    operators = (exact,)


class NullBooleanField(FieldType):
    field_class = forms.BooleanField
    operators = (exact, null, notnull)


class ChoiceField(FieldType):
    field_class = forms.ChoiceField
    operators = (exact, notexact, null, notnull)


class ModelChoiceField(ChoiceField):
    field_class = forms.ModelChoiceField


class MultipleChoiceField(FieldType):
    field_class = forms.MultipleChoiceField
    operators = (inlist, notinlist)


class ModelMultipleChoiceField(MultipleChoiceField):
    field_class = forms.ModelMultipleChoiceField


class ListField(FieldType):
    widget = forms.Textarea
    operators = (inlist, notinlist)


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
