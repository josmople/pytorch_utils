def glob(pathname, *, recursive=False, key=None, reverse=False):
    from glob import glob as _glob
    return sorted(_glob(pathname, recursive=recursive), key=key, reverse=reverse)


def prepare_dir(*paths):
    from os.path import join, dirname, exists, isfile
    from os import makedirs
    path = join(*paths)
    dirpath = dirname(path)
    if not exists(dirpath) or isfile(dirpath):
        makedirs(dirpath)
    return path
