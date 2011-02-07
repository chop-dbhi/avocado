from django.template import Context
from django.template.loader import get_template

from avocado.models import Column, Criterion, Field

FIELD_TEMPLATE_PATH = 'avocado/field-doc'
CONCEPT_TEMPLATE_PATH = 'avocado/concept-doc'

def generate_field_doc(pk, template_name=None, mimetype='txt'):
    "Generates the documentation for a single public field"
    try:
        field = Field.objects.get(pk=pk)
    except Field.DoesNotExist:
        return ''

    if template_name is None:
        template_name = '%s.%s' % (FIELD_TEMPLATE_PATH, mimetype)

    t = get_template(template_name)
    c = Context({'field': field})

    return t.render(c)

def generate_fields_doc(template_name=None, mimetype='txt'):
    "Generates the documentation for all fields"
    content = ''
    queryset = Field.objects.public()

    for f in queryset:
        content += generate_field_doc(f.pk, template_name, mimetype)
    return content

def generate_criterion_doc(pk, template_name=None, mimetype='txt'):
    "Generates the documentation for a single public criterion"
    try:
        criterion = Criterion.objects.get(pk=pk)
    except Criterion.DoesNotExist:
        return ''

    if template_name is None:
        template_name = '%s.%s' % (CONCEPT_TEMPLATE_PATH, mimetype)

    t = get_template(template_name)
    c = Context({
        'concept': criterion
    })

    return t.render(c)

def generate_criteria_doc(template_name=None, mimetype='txt'):
    content = ''
    queryset = Criterion.objects.public().order_by('order')

    for c in queryset:
        content += generate_criterion_doc(c.pk, template_name, mimetype)
    return content

def generate_column_doc(pk, template_name=None, mimetype='txt'):
    "Generates the documentation for a single public column"
    try:
        column = Column.objects.get(pk=pk)
    except Column.DoesNotExist:
        return ''

    if template_name is None:
        template_name = '%s.%s' % (CONCEPT_TEMPLATE_PATH, mimetype)

    t = get_template(template_name)
    c = Context({
        'concept': column
    })

    return t.render(c)

    pass

def generate_columns_doc(template_name=None, mimetype='txt'):
    content = ''
    queryset = Column.objects.public().order_by('order')

    for c in queryset:
        content += generate_column_doc(c.pk, template_name, mimetype)
    return content
