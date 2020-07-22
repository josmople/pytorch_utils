
from .strf import mformat, vformat, format


def eprint(*args, **kwds):
    from sys import stderr
    print(*args, file=stderr, **kwds)


def folder(*paths, prepare=True):
    from os.path import join, dirname
    path = join(*paths)
    path = dirname(path)
    if prepare:
        from os import makedirs
        makedirs(path, exist_ok=True)
    return path


def ts(template="%Y-%m-%d %H-%M-%S.%f"):
    from datetime import datetime
    now = datetime.now()
    path = now.strftime(template)
    return path


def context(raw=None):
    from .ctx import Data
    return Data(raw or {})


def context_interpreter(raw=None):
    from .ctx import Interpreter
    return Interpreter(raw or {})


def directory(*paths, ctx=None, formatter=None, auto_mkdir=True, auto_norm=True):
    from .ctx import Context
    if not isinstance(ctx, Context):
        ctx = context_interpreter(ctx or {})

    formatter = formatter or mformat

    from .dirp import ContextDirp
    return ContextDirp(*paths, ctx=ctx, formatter=formatter, auto_mkdir=auto_mkdir, auto_norm=auto_norm)


def logger(dirpath="/", ctx=None, formatter=None, auto_mkdir=True, auto_norm=True):
    from .log.pytorch import PyTorchLogger
    dirp = directory(str(dirpath), ctx=ctx, formatter=formatter, auto_mkdir=auto_mkdir, auto_norm=auto_norm)
    return PyTorchLogger(dirp)
