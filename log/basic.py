def eprint(*args, **kwds):
    from sys import stderr
    print(*args, file=stderr, **kwds)


def folder(*paths):
    from os.path import join, dirname
    path = join(*paths)
    path = dirname(path)
    from os import makedirs
    makedirs(path, exist_ok=True)
    return path


def timestamp(template="%Y-%m-%d %H-%M-%S.%f"):
    from datetime import datetime
    now = datetime.now()
    path = now.strftime(template)
    return path
