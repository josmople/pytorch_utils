# Running Queue

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


def backup(srcdir, destdir, copy_list, symlink_list):
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


class FileBound:

    def __init__(self, fpath):
        self.fpath = fpath

        try:
            with open(path, 'x'):
                pass
        except FileExistsError:
            pass

    def read(self):
        with open(self.fpath, "r") as f:
            return f.read()

    def write(self, text):
        with open(self.fpath, "w+") as f:
            if isinstance(text, (list, tuple)):
                return f.writelines(text)
            return f.write(text)

    def __call__(self, text=None):
        if text is None:
            return self.read()
        return self.write(text)


class Head:

    def __init__(self, path):
        self.fpath = path

        try:
            open(path, 'x')
        except FileExistsError:
            pass

    def __call__(self, text=None):
        if text is None:
            with open(self.fpath, "r") as f:
                return f.read()

        with open(self.fpath, "w+") as f:
            f.write(text)

    def __str__(self):
        return self()

    def __repr__(self):
        return f"{self.__class__.__name__}(fpath={self.fpath})"


class Strip:

    def __init__(self, path):
        self.fpath = path

        try:
            open(path, 'x')
        except FileExistsError:
            pass

    def __call__(self):
        from uuid import uuid4

        with open(self.fpath, "r") as f:
            lines = f.readlines()
            now = None if len(lines) == 0 else lines[-1].strip()

        with open(self.fpath, "a+") as f:
            nxt = str(uuid4())
            f.write(nxt + "\n")
            return now, nxt

    def __str__(self):
        return str(f.readlines())

    def __repr__(self):
        return f"{self.__class__.__name__}(fpath={self.fpath})"


def block(mark, target, interval=10):
    if target is None:
        return
    if isinstance(mark, str):
        mark = Head(mark)
    from time import sleep
    while str(mark) != str(target):
        sleep(interval)


def write(mark, text=None):
    if text is None:
        try:
            filepath = mark.fpath if isinstance(mark, Head) else str(mark)
            open(filepath, 'x')
        except FileExistsError:
            pass

    if isinstance(mark, str):
        mark = Head(mark)
    mark(text)


def run(src, dest, cmd, files, links, marker, start_code, end_code, interval=10):
    from atexit import register
    from os import system

    if not isinstance(marker, Head):
        marker = Head(str(marker))

    register(lambda: write(marker, end_code))

    block(marker, start_code, interval)
    backup(src, dest, files, links)
    system(f"cd {dest} && echo %cd% && {cmd}")
    write(marker, end_code)


def sequence(filepath):
    from uuid import uuid4

    try:
        open(filepath, 'x')
    except FileExistsError:
        pass

    with open(filepath, "r") as f:
        lines = f.readlines()
        now = None if len(lines) == 0 else lines[-1].strip()

    with open(filepath, "a+") as f:
        nxt = str(uuid4())
        f.write(nxt + "\n")
        return now, nxt
