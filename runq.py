# Running Queue

class Lock:

    # TODO Order
    def __init__(self, dirpath, key=None, order=None, queuefile="queue.txt", headfile="head.txt", interval=2):
        from os import makedirs
        makedirs(dirpath, exist_ok=True)

        from os.path import join
        self.queuefile = join(dirpath, queuefile)
        self.headfile = join(dirpath, headfile)
        self.interval = interval

        if key is None:
            from uuid import uuid4
            key = uuid4()
        self.key = key = str(key)

        from atexit import register
        register(self.close)

        # TODO Possible Error
        self.queue = list(self.queue) + [self.key]

        if self.head is None:
            self.head = self.key

        from time import sleep
        while self.head != self.key:
            sleep(self.interval)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self):
        self.queue = list(filter(lambda v: v != self.key, self.queue))

        if self.head == self.key:
            self.head = self.queue[0] if len(self.queue) > 0 else ""

        from atexit import unregister
        unregister(self.close)

    def _register(self, order):
        from os.path import exists, isdir
        if not exists(self.queuefile) or isdir(self.queuefile):
            open(self.queuefile, "x").close()

        with open(self.queuefile, "r+") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                lines[i] = line.strip()
            return tuple(lines)

    @property
    def queue(self):
        from os.path import exists, isdir
        if not exists(self.queuefile) or isdir(self.queuefile):
            open(self.queuefile, "x").close()

        with open(self.queuefile, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                lines[i] = line.strip()
            return tuple(lines)

    @queue.setter
    def queue(self, keys):
        with open(self.queuefile, "w+") as f:
            lines = []
            for v in keys:
                lines.append(str(v) + "\n")
            f.writelines(lines)

    @property
    def head(self):
        from os.path import exists, isdir
        if not exists(self.headfile) or isdir(self.headfile):
            open(self.headfile, "x").close()

        with open(self.headfile, "r") as f:
            val = f.read()
            return None if val is "" else val

    @head.setter
    def head(self, key):
        with open(self.headfile, "w+") as f:
            f.write(key)


def relative(fn):

    from functools import wraps
    from os.path import relpath, join

    def new_fn(srcdir, destdir, paths):
        for src in paths:
            path = relpath(srcdir, src)
            dest = join(destdir, path)
            fn(src, dest)

    return new_fn


def copy(src, dest):
    from os.path import isdir, dirname
    from shutil import copyfile, copytree
    from os import makedirs

    if isdir(src):
        return copytree(src, dest)

    makedirs(dirname(dest), exist_ok=True)
    return copyfile(src, dest)


def symlink(src, dest):
    from os.path import isdir, dirname, normpath
    from os import makedirs, symlink

    if isdir(src):
        makedirs(dirname(normpath(dest)), exist_ok=True)
        return symlink(src, dest, target_is_directory=True)

    makedirs(dirname(dest), exist_ok=True)
    return symlink(src, dest)


def clone(srcdir, destdir, copy_list, symlink_list):
    from os import makedirs
    from os.path import relpath, join, abspath

    makedirs(destdir, exist_ok=True)

    for src in copy_list:
        path = relpath(src, srcdir)
        dest = join(destdir, path)

        copy(abspath(src), abspath(dest))

    for src in symlink_list:
        path = relpath(src, srcdir)
        dest = join(destdir, path)

        symlink(abspath(src), abspath(dest))


def run(_, *args, **kwds):
    from os import system
    return system(_.format(*args, **kwds))


lock = Lock
