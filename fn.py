import typing as _T
from torch.nn import Module as _Module

_Fn = _T.TypeVar("_Fn")


class instanceclassmethod(object):
    """
    The method should take two arguments, 'self' and 'cls'.
    The value of 'self' is None if invoked as a classmethod.
    """

    def __init__(self, func: _Fn):
        self.func = func

    def __get__(self, instance, clas=None) -> _Fn:
        from functools import wraps

        @wraps(self.func)
        def func(*args, **kwds):
            return self.func(instance, clas, *args, **kwds)

        return func


def ignore_unmatched_kwargs(f):
    """Make function ignore unmatched kwargs.

    If the function already has the catch all **kwargs, do nothing.

    From: https://stackoverflow.com/a/63787701
    """
    from inspect import Parameter, signature
    import functools

    if any(param.kind == Parameter.VAR_KEYWORD for param in signature(f).parameters.values()):
        return f
    #

    @functools.wraps(f)
    def inner(*args, **kwargs):
        # For each keyword arguments recognised by f, take their binding from **kwargs received
        filtered_kwargs = {
            name: kwargs[name]
            for name, param in signature(f).parameters.items()
            if name in kwargs
            and (
                param.kind is Parameter.KEYWORD_ONLY or
                param.kind is Parameter.POSITIONAL_OR_KEYWORD
            )
        }
        return f(*args, **filtered_kwargs)
    return inner


def as_pytorch_module(fn: _Fn = None, *, include_self=False) -> _T.Union[type, _T.Callable[[], _T.Union[_Fn, _Module]]]:
    """
    Transforms functions to torch.nn.Module
    """
    if fn is None:
        from functools import partial
        return partial(as_pytorch_module, include_self=include_self)

    from torch.nn import Module

    if include_self:
        def forward(self, *args, **kwds):
            return fn(self, *args, **kwds)
    else:
        def forward(self, *args, **kwds):
            return fn(*args, **kwds)

    return type(f"LambdaModule__{fn.__name__}", (Module, ), dict(forward=forward))


del _Module, _T, _Fn
