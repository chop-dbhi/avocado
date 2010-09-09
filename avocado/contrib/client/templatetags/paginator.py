from django import template
from django.template import Variable
from django.template.loader import get_template

register = template.Library()

@register.tag
def render_paginator(parser, token):
    toks = token.split_contents()
    toks.pop(0) # pop tag name
    for i,t in enumerate(toks):
        toks[i] = t.strip('"').strip("'")
    return RenderPaginator(*toks)


class RenderPaginator(template.Node):
    def __init__(self, template_name, first_last_amount=0,
        before_after_amount=2):

        self.template_name = template_name
        self.first_last_amount = int(first_last_amount)
        self.before_after_amount = int(before_after_amount)

    def render(self, context):
        page_obj = Variable('page_obj').resolve(context)
        paginator = Variable('paginator').resolve(context)
        page_numbers = []

        # only process if the current page number is greater than the number of
        # required links.
        if page_obj.number > (self.first_last_amount + self.before_after_amount + 1):
            # append first pages, e.g. [1, 2] if `first_last_amount' is 2
            for i in range(1, self.first_last_amount + 1):
                page_numbers.append(i)

            page_numbers.append(None)
            # append the leading pages relative to the current page, e.g.
            # [10, 11] if `before_after_amount' is 2 and current page is 12
            for i in range(page_obj.number - self.before_after_amount, page_obj.number):
                page_numbers.append(i)

        else:
            for i in range(1, page_obj.number):
                page_numbers.append(i)

        # if there is still a gap until `paginator.num_pages' is reached, add trailing pages
        if (page_obj.number + self.first_last_amount + self.before_after_amount + 1) < paginator.num_pages:
            for i in range(page_obj.number, page_obj.number + self.before_after_amount + 1):
                page_numbers.append(i)

            page_numbers.append(None)
            for i in range(paginator.num_pages + 1 - self.first_last_amount, paginator.num_pages + 1):
                page_numbers.append(i)

        else:
            for i in range(page_obj.number, paginator.num_pages + 1):
                page_numbers.append(i)

        t = get_template(self.template_name)
        context.update({
            'page_numbers': page_numbers,
        })
        return t.render(context)
