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


def directory(*paths, ctx=None, formatter=None, auto_mkdir=True, auto_norm=True):
    from dirp import ContextDirp

    if ctx is None:
        ctx = {}
        # TODO

    if formatter is None:
        from strf import mformat
        formatter = mformat

    return ContextDirp(*paths, ctx=ctx, formatter=formatter, auto_mkdir=auto_mkdir, auto_norm=auto_norm)
