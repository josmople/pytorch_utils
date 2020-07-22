from .context import *
from .functional import *
from . import values

Data = factory()
Interpreter = factory(use_cval=True)


def create_context(raw=None):
    raw = raw or {}
    return Data(raw), Interpreter(raw)
