import typing as _T

Fn = _T.TypeVar("Fn")


class instanceclassmethod(object):
    """
    The method should take two arguments, 'self' and 'cls'.
    The value of 'self' is None if invoked as a classmethod.
    """

    def __init__(self, func: Fn):
        self.func = func

    def __get__(self, instance, clas=None) -> Fn:
        from functools import wraps

        @wraps(self.func)
        def func(*args, **kwds):
            return self.func(instance, clas, *args, **kwds)

        return func


del _T, Fn
