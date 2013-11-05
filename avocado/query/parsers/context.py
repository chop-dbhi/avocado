import logging
from django.core.exceptions import ValidationError
from avocado.query import operators
from avocado.query.validators import Validator, FieldValidator
from avocado.models import DataContext

__all__ = ('BranchParser', 'ConditionParser', 'CompositeParser', 'TreeParser')


BRANCH_TYPES = ('and', 'or')

log = logging.getLogger(__name__)


def has_keys(data, keys):
    "Return true is all keys are present in data."
    for key in keys:
        if key not in data:
            return False
    return True


def is_branch(data):
    "Validates required structure for a branch node."
    return has_keys(data, ('type', 'children'))


def is_condition(data):
    "Validates required structure for a condition node."
    return has_keys(data, keys=('operator', 'value'))


def is_composite(data):
    "Validates required structure for a composite node."
    return 'composite' in data


def get_parser(data):
    if not data or not isinstance(data, dict):
        return
    if is_composite(data):
        return CompositeParser
    elif is_condition(data):
        return ConditionParser
    elif is_branch(data):
        return BranchParser


class BranchParser(Validator):
    "Parser and validator for context branch nodes."

    error_messages = {
        'invalid_branch_type': 'the branch type is invalid',
    }

    warning_messages = {
        'empty_branch': 'the branch contains no children',
        'invalid_child': 'one or more child nodes are invalid',
    }

    error_messages.update(Validator.error_messages)
    warning_messages.update(Validator.warning_messages)

    fields = ('type', 'children')

    def validate_type(self):
        "Validates the branch type."
        branch_type = self.data.get('type', '').lower()
        if branch_type not in BRANCH_TYPES:
            self.error('invalid_branch_type')
        return branch_type

    def validate_children(self):
        """Recurses validation to children in branch.

        Note this occurs regardless if this node is disabled (or if there
        are warnings), to enable downstream handling.
        """
        children = self.data.get('children')
        cleaned_children = []

        if children:
            for child in children:
                parser = get_parser(child)
                if not parser:
                    self.warn('invalid_child')
                    continue
                cleaned_children.append(parser(child, **self.context))
        else:
            self.warn('empty_branch')
        return cleaned_children


class ConditionParser(FieldValidator):
    error_messages = {
        'invalid_value_type': 'invalid value type for field',
        'invalid_operator': 'invalid operator for field',
        'invalid_operator_for_value': 'invalid operator for value',
    }

    warning_messages = {
        'value_out_of_range': 'value out of range',
        'value_not_a_choice': 'value not a choice',
        'field_not_nullable': 'the field is not nullable',
    }

    error_messages.update(FieldValidator.error_messages)
    warning_messages.update(FieldValidator.warning_messages)

    fields = ('concept', 'field', 'value', 'operator', 'nulls')

    def validate_value(self):
        "Checks the value is valid for the field."
        field = self.cleaned_data.get('field')

        if not field:
            return

        try:
            return field.to_python(self.data.get('value'))
        except ValidationError:
            self.error('invalid_value_type')

    def validate_operator(self):
        "Checks the operator is valid for the field"
        field = self.cleaned_data.get('field')

        if not field:
            return

        operator = self.data.get('operator')

        # Check if this is a valid operator for the field
        if operator not in field.operators:
            self.error('invalid_operator')

        # Double check this is also registered (in case the above
        # operators are not built-ins)
        if operator not in operators.registry:
            log.error('Operator {0} locally defined, but not in the registry'
                      .format(operator))
            self.error('invalid_operator')

        return operators.registry.get(operator)

    def validate_nulls(self):
        field = self.cleaned_data.get('field')

        if not field:
            return

        nulls = self.data.get('nulls')
        if nulls and not field.nullable:
            self.warn('field_not_nullable')
        return nulls


class CompositeParser(Validator):
    error_messages = {
        'context_does_not_exist': 'the context does not exist',
    }

    warning_messages = {
        'context_not_defined': 'the context is not defined',
    }

    error_messages.update(Validator.error_messages)
    warning_messages.update(Validator.warning_messages)

    fields = ('context',)

    def validate_context(self):
        context = self.data.get('context')

        if not context:
            self.warn('context_not_defined')

        kwargs = {'pk': context}
        if 'user' in self.context:
            kwargs = {'user': self.context['user']}

        try:
            return DataContext.objects.get(**kwargs)
        except DataContext.DoesNotExist:
            self.error('context_does_not_exist')


class TreeParser(Validator):
    error_messages = {
        'invalid': 'invalid data',
    }

    def validate(self):
        parser = get_parser(self.data)
        if parser:
            self.cleaned_data['tree'] = parser(self.data, **self.context)
        else:
            self.error('invalid')
