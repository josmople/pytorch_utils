# Running Queue

class Lock:

    def __init__(self, dirpath, key=None, order=None, queuefile="queue.txt", headfile="head.txt", interval=2):
        from os import makedirs
        makedirs(dirpath, exist_ok=True)

        from os.path import join
        self.queuefile = join(dirpath, queuefile)
        self.headfile = join(dirpath, headfile)
        self.interval = interval
        self.order = order

        if key is None:
            from uuid import uuid4
            key = uuid4()
        self.key = key = str(key)

        from atexit import register
        register(self.close)

        self._register(key, order)
        self._check(key)

        from time import sleep
        while self.head != key:
            sleep(self.interval)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def _write(self, file, content):
        file.seek(0)
        file.write(content)
        file.truncate()

    def _initfile(self, path):
        from os.path import exists, isdir
        if not exists(path) or isdir(path):
            open(path, "x").close()

    def close(self):
        with open(self.queuefile, "r+") as fq:
            lines = map(str.strip, fq.readlines())
            lines = list(filter(lambda v: v != self.key, lines))

            content = str.join("\n", lines)
            self._write(fq, content)

            with open(self.headfile, "r+") as fh:
                head = fh.read().strip()
                if head == self.key:
                    head = lines[0] if len(lines) > 0 else ""
                    self._write(fh, head)

        from atexit import unregister
        unregister(self.close)

    def _register(self, key, order):
        self._initfile(self.queuefile)

        with open(self.queuefile, "r+") as f:
            lines = list(map(str.strip, f.readlines()))
            assert key not in lines, "The key is already registered"

            if order is None:
                lines.append(key)
            else:
                lines.insert(order, key)

            content = str.join("\n", lines)
            self._write(f, content)

    def _check(self, key):
        self._initfile(self.headfile)

        with open(self.headfile, "r+") as fh:
            head = fh.read().strip()
            if head is "":
                self._write(fh, key)

    @property
    def queue(self):
        with open(self.queuefile, "r") as fq:
            vals = map(str.strip, fq.readlines())
            return tuple(vals)

    @property
    def head(self):
        with open(self.headfile, "r") as fh:
            val = fh.read()
            return None if val is "" else val


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


def run(command, srcdir=".", destdir=".", copy_list=None, symlink_list=None, lockdir="lock/", template="cd {destdir} && {command}", **kwds):
    from os import system
    clone(srcdir, destdir, copy_list or [], symlink_list or [])

    command_format = template if callable(template) else (lambda **args: str(template).format(**args))

    with Lock(lockdir, **kwds) as l:
        system(command_format(
            command=command,
            srcdir=srcdir,
            destdir=destdir,
            copy_list=copy_list,
            symlink_list=symlink_list,
            template=template,
            **kwds
        ))
