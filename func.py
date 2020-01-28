def no_grad(fn):
    from torch import no_grad
    from functools import wraps

    @wraps(fn)
    def no_grad_fn(*args, **kwargs):
        with no_grad():
            return fn(*args, **kwargs)

    return no_grad_fn
