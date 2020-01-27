from abc import ABC as _ABC, abstractmethod as _abstractmethod


class PathResolution(_ABC):

    @property
    @_abstractmethod
    def dirpath(self):
        pass

    @classmethod
    @_abstractmethod
    def __call__(self):
        pass


class LogDir(PathResolution):

    dirpath = ""

    def __init__(self, *paths, default_prepare=True, default_meta=None):
        from os.path import join
        self.dirpath = join(*paths, "")
        self.default_prepare = default_prepare
        self.default_meta = default_meta

    def __call__(self, *paths, prepare=None, meta=None):
        from os.path import join, dirname, exists, isfile, normpath
        from os import makedirs

        path = join(self.dirpath, *paths)

        if meta is None:
            meta = self.default_meta
        if meta is not None:
            if callable(meta):
                meta = meta()
            path = path.format(**meta)

        if prepare is None:
            prepare = self.default_prepare
        if prepare:
            dirpath = dirname(path)
            if not exists(dirpath) or isfile(dirpath):
                makedirs(dirpath)

        return normpath(path)


def timestamp(template="%Y-%m-%d %H-%M-%S.%f"):
    from datetime import datetime
    now = datetime.now()
    path = now.strftime(template)
    return path


def log_metric(tag, value, step):
    pass
