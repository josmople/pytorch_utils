from os.path import *

from os import makedirs


def glob(pathname, *, recursive=False, unique=True, sort=True, sort_key=None, sort_reverse=False):
    from glob import glob as _glob

    # If simple string
    if isinstance(pathname, str):
        return sorted(_glob(pathname, recursive=recursive), key=sort_key, reverse=sort_reverse)

    # Assume pathname is iterable
    assert all([isinstance(p, str) for p in pathname]), "pathname must be a string or string[]"

    values = []
    for path in pathname:
        values += _glob(path, recursive=recursive)

    if unique:
        from collections import OrderedDict
        values = OrderedDict.fromkeys(values).keys()

    if sort:
        return sorted(values, key=sort_key, reverse=sort_reverse)

    return values
