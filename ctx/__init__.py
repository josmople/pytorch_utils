from .context import Context, ContextValue, factory
from .functional import *
from . import values

Data = factory()
Interpreter = factory(use_cval=True)


def _create_context_default_fn(k):
    raise ValueError(f"Default value is not set: Key '{k}' is missing")


def create_context(raw=None, default_fn=_create_context_default_fn):
    raw = raw or {}
    if default_fn is not None:
        raw["__default__"] = vfn(default_fn)
    return Data(raw), Interpreter(raw)


del _create_context_default_fn
