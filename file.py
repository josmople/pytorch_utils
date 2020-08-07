def read_text(path, **kwds):
    with open(path, "r", **kwds) as f:
        return f.read()


def write_text(path, text, **kwds):
    with open(path, "w+", **kwds) as f:
        return f.write(text)


def read_lines(path, keepends=False, **kwds):
    return read_text(path, **kwds).splitlines(keepends)


def write_lines(path, lines, linesep=None, **kwds):
    return write_text(path, (linesep or "\n").join(lines), **kwds)


def file_exists(path):
    from os.path import exists, isfile
    return exists(path) and isfile(path)


def dir_exists(path):
    from os.path import exists, isdir
    return exists(path) and isdir(path)
