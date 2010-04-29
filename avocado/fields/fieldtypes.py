"""
Set of classes that provide a means of generating, validating and cleaning
two form fields that define the `operator' and `value' defined by the user.

In most cases, only certain operators make sense to be utilized by certain
FieldType subclasses, but this method provides a means to be more restrictive
on what operators are allowed.


"""

from django import forms
from avocado.fields.operators import *


class OperatorNotPermitted(Exception):
    pass


class FieldType(object):
    field = forms.CharField
    widget = None
    operators = ()
    
    def __init__(self):
        if not self.operators:
            raise NotImplementedError, 'subclasses must have at least one ' \
                'operator associated with it'

    def _get_operator(self, operator):
        for x in self.operators:
            if x.operator == operator:
                return x
        raise OperatorNotPermitted, '%s is not permitted for field type %s' % \
            (operator, self.__class__.__name__)

    def clean(self, formfield, value, operator):
        try:
            cleaned_value = self._field.clean(value)
        op_obj = self._get_operator(operator)
        
        try:
            validated_value = op_obj.clean(value)
        except ValidationError, e:
            return (False, None, [str(e)])

        try:
            cleaned_value = self._field.clean(validated_value)
        except forms.ValidationError, e:
            return (False, None, [str(e)]) # TODO return list of error strings, not html
        
        return (True, cleaned_value, ())


class CharField(FieldType):
    operators = (iexact, notiexact, contains, doesnotcontain)


class ListField(FieldType):
    widget = forms.Textarea
    operators = (inlist, notinlist)


class ChoiceField(FieldType):
    field = forms.ChoiceField
    operators = (exact, notexact)


class MultipleChoiceField(FieldType):
    field = forms.MultipleChoiceField
    operators = (inlist, notinlist)


class ModelChoiceField(ChoiceField):
    field = forms.ModelChoiceField


class ModelMultipleChoiceField(MultipleChoiceField):
    field = forms.ModelMultipleChoiceField


class IntegerField(FieldType):
    field = forms.IntegerField
    operators = (exact, notexact, lt, lte, gt, gte, between, notbetween, null,
        notnull)


class DecimalField(IntegerField):
    field = forms.DecimalField


class DateField(IntegerField):
    field = forms.DateField


class BooleanField(FieldType):
    field = forms.NullBooleanField
    operators = (exact, null, notnull)