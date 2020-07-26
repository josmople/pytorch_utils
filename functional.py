from .events import Event
from .strf import format
from .search import glob


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


def context(raw=None, cval=True):
    if raw is None:
        from os import getcwd
        raw = {}
        raw["wd"] = getcwd()
        raw["ts"] = ts()

    from .ctx import Data, Interpreter
    if cval:
        return Interpreter(raw)
    return Data(raw)


def directory(*paths, ctx=None, formatter=None, auto_mkdir=True, auto_norm=True):
    from .dirp import ContextDirp, context_dirp_formatter
    return ContextDirp(
        *paths,
        ctx=ctx or {},
        formatter=formatter or context_dirp_formatter,
        auto_mkdir=auto_mkdir,
        auto_norm=auto_norm
    )


def pytorch_logger(dirpath="/", ctx=None, ctx_attr="ctx", formatter=None, auto_mkdir=True, auto_norm=True):
    ctx = ctx or context(cval=True)
    dirp = directory(
        str(dirpath),
        ctx=ctx,
        formatter=formatter,
        auto_mkdir=auto_mkdir,
        auto_norm=auto_norm
    )
    from .log.pytorch import PyTorchLogger
    logger = PyTorchLogger(dirp)
    setattr(logger, ctx_attr, ctx)
    return logger
