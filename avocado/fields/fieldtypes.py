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

def _operator_dict(*args):
    return dict(map(lambda x: (x.operator, x), args))

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
    
    def validate(self, operator, value, model_field_obj=None):
        # 1. verify operator is allowed
        try:
            op_obj = _get_operator(operator)
        except OperatorNotPermitted, e:
            raise ValidationError, e.message
        
        # 2. check special case for `null' or `notnull'
        fc = self.field_class
        if op_obj in (null, notnull):
            fc = forms.BooleanField

        # 3. clean value according to model field formfield
        if model_field_obj:
            formfield = model_field_obj.formfield(form_class=fc)
        else:
            formfield = fc()
        
        clean_value = formfield.clean(value)
        
        # 4. validate cleaned value is appropriate for the operator
        op_obj.validate(clean_value)
        
        return clean_value

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