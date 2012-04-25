from django.core.exceptions import ValidationError
from avocado.models import DataField

BRANCH_KEYS = ('children', 'type')
CONDITION_KEYS = ('id', 'operator', 'value')
LOGICAL_OPERATORS = ('and', 'or')


def has_keys(obj, keys):
    "Check the required keys are present in `obj` for this node type."
    for key in keys:
        if key not in obj:
            return False
    return True


def is_branch(obj):
    "Validates required structure for a branch node"
    if has_keys(obj, keys=BRANCH_KEYS):
        if obj['type'] not in LOGICAL_OPERATORS:
            raise ValidationError('Invalid logical operator between conditions')
        length = len(obj['children'])
        if length < 2:
            raise ValidationError('Invalid format. Branch node must contain two or more conditions')
        return True


def is_condition(obj):
    "Validates required structure for a condition node"
    if has_keys(obj, keys=CONDITION_KEYS):
        return True


def validate(id, operator, value, **context):
    """Takes a data field id (or natural key), operator and value and
    validates the condition.

    The `id` may be:
        - the primary key itself as an integer, e.g. 10
        - the natural key as a list of values, ['app', 'model', 'field']
        - the natural key as a dotted string, 'app.model.field'
    """
    try:
        if type(id) is int:
            datafield = DataField.objects.get(id=id)
        elif type(id) is str:
            datafield = DataField.objects.get_by_natural_key(*id.split('.'))
        else:
            datafield = DataField.objects.get_by_natural_key(*id)
    except DataField.DoesNotExist, e:
        raise ValidationError(e.message)
    return datafield.validate(operator, value, **context)


def parse(obj):
    if type(obj) is not dict:
        raise ValidationError('Object must be of type dict')
    if is_condition(obj):
        validate(**obj)
    elif is_branch(obj):
        map(lambda x: parse(x), obj['children'])
    else:
        raise ValidationError('Object neither a branch nor condition: {0}'.format(obj))
