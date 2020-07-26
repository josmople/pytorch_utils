from .context import Context, ContextValue, factory
from .functional import *
from . import values
from . import ops


class Data(factory()):

    def __init__(self, data=None, default=None):
        super().__init__(data)
        self(val=default)


def _interpreter_default_fn(k):
    raise ValueError(f"Default value is not set: Key '{k}' is missing")


class Interpreter(factory(use_cval=True)):

    def __init__(self, data=None, default=vfn(_interpreter_default_fn)):
        super().__init__(data)
        self(val=default)


del _interpreter_default_fn
