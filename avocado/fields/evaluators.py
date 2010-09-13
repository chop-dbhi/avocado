from functools import wraps

from avocado.utils.iter import ins

def _check_iter(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        val = func(*args, **kwargs)
        if not ins(val):
            raise TypeError
        for e in val:
            if not ins(e) or len(e) != 2:
                raise TypeError
        return tuple(val)
    return decorator

@_check_iter
def eval_choices(val):
    # try evaling a straight sequence in the format:
    #   [(1,'foo'), (2,'bar'), ...]
    try:
        return eval(val)
    except (SyntaxError, NameError):
        return None

@_check_iter
def model_attr(model, attr):
    # attempts to check the `model' for an attribute `attr':
    #   when: attr = SHAPE_CHOICES
    #   test: model.SHAPE_CHOICES
    return getattr(model, attr, None)

@_check_iter
def module_attr(module, attr):
    return getattr(module, attr, None)


def evaluate(mf):
    ch = mf.choices_handler
    funcs = (
        (model_attr, (mf.model, ch)),
        (module_attr, (mf.module, ch)),
        (eval_choices, (ch,)),
    )

    for func, attrs in funcs:
        try:
            choices = func(*attrs)
            break
        except TypeError:
            pass
    else:
        choices = None
    return choices
