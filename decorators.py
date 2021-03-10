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


def fn_module(fn: _Fn) -> _T.Callable[[], _T.Union[_Fn, _Module]]:
    from torch.nn import Module

    def forward(self, *args, **kwds):
        return fn(*args, **kwds)

    return type(f"FnModule__{fn.__name__}", (Module, ), dict(forward=forward))


del _Module, _T, _Fn
