from functools import wraps

from avocado.utils.iter import is_iter_not_string

def _check_iter(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        val = func(*args, **kwargs)
        if not is_iter_not_string(val):
            raise TypeError
        for e in val:
            if not is_iter_not_string(e) or len(e) != 2:
                raise TypeError
        return val
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


        