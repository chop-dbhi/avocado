import logging
from django.core.exceptions import ValidationError
from avocado.core import utils
from avocado.conf import settings
from avocado.models import DataConcept, DataField

log = logging.getLogger(__name__)


class Validator(object):
    error_messages = {}
    warning_messages = {}

    fields = ()

    def __init__(self, data, **context):
        # Copy of the input data, this will be updated as necessary reflecting
        # errors, warnings, and other changes.
        self.data = data.copy()

        # This represents the _cleaned_ representations of the input such
        # as model instances. Validators that depend on this upstream data
        # can check this to ensure the data has been cleaned.
        self.cleaned_data = {}

        # Contains the additional context pass into the validator that may be
        # used during validation.
        self.context = context

        self.errors = []
        self.warnings = []

    def _validate(self):
        """
        Performs valiation of fields defined in `fields`. Output will added to
        `cleaned_data`. Calls to `error` will prevent the output from being
        added.
        """
        for field in self.fields:
            method_name = 'validate_{0}'.format(field)
            if hasattr(self, method_name):
                try:
                    result = getattr(self, method_name)()
                    self.cleaned_data[field] = result
                except ValidationError:
                    pass

    def _post_validate(self):
        """Performs post-validation. If errors or warnings are present, the
        `enabled` flag gets toggled to reflect this.
        """
        # Remove previous annotations
        self.data.pop('errors', [])
        enabled = self.data.pop('enabled', True)
        warnings = self.data.pop('warnings', [])

        if self.errors:
            self.data['errors'] = self.errors
            enabled = False

        if self.warnings:
            self.data['warnings'] = self.warnings
            # If the warnings have changed from the previous state, force
            # the state to be disabled.
            if set(self.warnings) != set(warnings):
                enabled = False

        # Only set the flag if false or if warnings are still around for
        # revalidation.
        if not enabled or self.warnings:
            self.data['enabled'] = enabled

        # Copy data, update with cleaned output. This will expose the
        # objects
        cleaned_data = self.cleaned_data
        self.cleaned_data = self.data.copy()
        self.cleaned_data.update(cleaned_data)

    @property
    def validation_errors(self):
        messages = []
        for key in self.errors:
            if key in settings.VALIDATION_ERRORS:
                messages.append(settings.VALIDATION_ERRORS[key])
            elif key in self.validation_errors:
                messages.append(self.validation_errors[key])
            raise KeyError('No message for key: {0}'.format(key))
        return messages

    @property
    def validation_warnings(self):
        messages = []
        for key in self.warnings:
            if key in settings.VALIDATION_WARNINGS:
                messages.append(settings.VALIDATION_WARNINGS[key])
            elif key in self.validation_warnings:
                messages.append(self.validation_warnings[key])
            raise KeyError('No message for key: {0}'.format(key))
        return messages

    def error(self, key):
        "Adds an error message based on a message key."
        if key not in self.error_messages:
            raise KeyError('No validation error with key: {0}'.format(key))
        self.errors.append(key)
        raise ValidationError('noop')

    def warn(self, key):
        "Adds an warning message based on a message key."
        if key not in self.warning_messages:
            raise KeyError('No validation warning with key: {0}'.format(key))
        self.warnings.append(key)

    def validate(self):
        "Performs cross-data cleaning."

    def is_valid(self):
        "Performs full validation."
        self._validate()
        self.validate()
        self._post_validate()
        if self.errors:
            return False
        return True


class FieldValidator(Validator):
    error_messages = {
        'field_required': 'field required',
        'field_does_not_exist': 'the field does not exist',
        'field_does_not_exist_for_concept': 'the field does not exist for the '
                                            'specified concept',
        'ambiguous_field': 'the field lookup is ambiguous',
        'ambiguous_field_for_concept': 'the field lookup for the specified is '
                                       'ambiguous',
        'concept_does_not_exist': 'the concept does not exist',
        'concept_wrong_format': 'the concept lookup is not an id'
    }

    error_messages.update(Validator.error_messages)

    fields = ('concept', 'field')

    def validate_concept(self):
        concept = self.data.get('concept')

        if not concept:
            return

        # Ignore any concept that is not an explicit ID.
        try:
            kwargs = {'pk': int(concept)}
        except ValueError:
            self.error('concept_wrong_format')

        if 'user' in self.context:
            queryset = DataConcept.objects.published(user=self.context['user'])
        else:
            queryset = DataConcept.objects.all()

        try:
            return queryset.get(**kwargs)
        except DataConcept.DoesNotExist:
            self.error('concept_does_not_exist')

    def validate_field(self):
        """
        Validate and clean the field.

        If a concept is also available, it will accessible via `self.concept`.
        """
        field = self.data.get('field')

        if not field:
            self.error('field_not_defined')

        concept = self.cleaned_data.get('concept')

        # A non-falsy concept is defined, but no cleaned concept is available.
        # The field cannot be validated
        if self.data.get('concept') and not concept:
            return

        kwargs = utils.parse_field_key(field)

        # If the concept is defined, restrict to the concept, otherwise
        # get from the entire set.
        if concept:
            queryset = concept.fields.all()
        elif 'user' in self.context:
            queryset = DataField.objects.published(user=self.context['user'])
        else:
            queryset = DataField.objects.all()

        try:
            return queryset.get(**kwargs)
        except DataField.DoesNotExist:
            if concept:
                self.error('field_does_not_exist_for_concept')
            self.error('field_does_not_exist')
        except DataField.MultipleObjectsReturned:
            if concept:
                self.error('ambiguous_field_for_concept')
            self.error('ambiguous_field')
