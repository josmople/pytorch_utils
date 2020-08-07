def read_text(path, **kwds):
    with open(path, "r", **kwds) as f:
        return f.read()


def write_text(path, text, **kwds):
    with open(path, "w+", **kwds) as f:
        return f.write(text)


def read_lines(path, **kwds):
    from os import linesep
    with open(path, "r", **kwds) as f:
        return list(map(lambda s: s.strip(linesep), f.readlines()))


def write_lines(path, lines, **kwds):
    from os import linesep
    text = str.join(linesep, lines)
    with open(path, "w+", **kwds) as f:
        return f.write(text)


def file_exists(path):
    from os.path import exists, isfile
    return exists(path) and isfile(path)


def dir_exists(path):
    from os.path import exists, isdir
    return exists(path) and isdir(path)
