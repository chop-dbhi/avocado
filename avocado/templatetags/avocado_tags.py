from django import template
from avocado.models import DataField, DataConcept


register = template.Library()


class AvocadoLoadNode(template.Node):
    def __init__(self, model, key, variable):
        self.model = model
        self.key = key
        self.variable = variable

    def render(self, context):
        try:
            if type(self.key) is int:
                obj = self.model.objects.get(pk=self.key)
            else:
                obj = self.model.objects.get_by_natural_key(self.key)
            context[self.variable] = obj
        except self.model.DoesNotExist:
            pass
        return ''


def do_avocado(parser, token):
    """Loads a DataField or DataConcept instance.

    Examples:

        # Get the datafield with a primary key 30
        {% avocado load field 30 as foo %}

        # Get the datafield with a natural key "blog.tag.label"
        {% avocado load field "blog.tag.label" as tag %}

        # Get the dataconcept with a primary key 14
        {% avocado load concept 14 as bar %}
    """

    toks = token.split_contents()

    if len(toks) != 6:
        raise template.TemplateSyntaxError(u'{0} tag requires 6 arguments'
                                           .format(toks[0]))

    tag_name, operation, model, key, _as, variable = toks

    if operation != 'load':
        raise template.TemplateSyntaxError(u'{0} {1} is an invalid operation'
                                           .format(tag_name, operation))

    if model == 'field':
        model = DataField
    elif model == 'concept':
        model = DataConcept
    else:
        raise template.TemplateSyntaxError(u'{0} ... {1} is not a valid model '
                                           'type'.format(tag_name, model))

    if key.isdigit():
        key = int(key)
    else:
        if model is DataConcept:
            raise template.TemplateSyntaxError(u'{0} ... concept only '
                                               'supports primary keys.'
                                               .format(tag_name))
        if key[0] != key[1] and key[0] not in ('"', "'"):
            raise template.TemplateSyntaxError(u'{0} ... {1} natural keys '
                                               'must be quoted'
                                               .format(tag_name, key))
        key = key[1:-1]

    return AvocadoLoadNode(model, key, variable)


register.tag('avocado', do_avocado)
