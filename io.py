def glob(pathname, *, recursive=False, key=None, reverse=False):
    from glob import glob as _glob

    # If simple string
    if isinstance(pathname, str):
        return sorted(_glob(pathname, recursive=recursive), key=key, reverse=reverse)

    # Assume pathname is iterable
    assert all([isinstance(p, str) for p in pathname]), "pathname must be a string or string[]"

    values = []
    for path in pathname:
        values += _glob(path, recursive=recursive)
    return sorted(values, key=key, reverse=reverse)


def prepare_dir(*paths):
    from os.path import join, dirname, exists, isfile
    from os import makedirs
    path = join(*paths)
    dirpath = dirname(path)
    if not exists(dirpath) or isfile(dirpath):
        makedirs(dirpath)
    return path
