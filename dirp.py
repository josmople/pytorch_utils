import typing as _T


def ts(template: str = "%Y-%m-%d %H-%M-%S.%f") -> str:
    from datetime import datetime
    template = str(template)
    now = datetime.now()
    path = now.strftime(template)
    return path


def join(*paths: str):
    from os.path import join as _join
    return _join(*[str(p) for p in paths])


def format(path, values: _T.Union[_T.Mapping, _T.Callable[[], _T.Mapping]]):
    from .strf import default_vformat
    record = values
    if callable(values):
        record = values()
    return default_vformat(path, args=[], kwargs=record)


def makedirs(path: str):
    from os import makedirs as _makedirs
    from os.path import dirname
    path = str(path)
    pathdir = dirname(path)
    if pathdir == "":
        pathdir = "."
    _makedirs(pathdir, exist_ok=True)
    return pathdir


class Dirpath:

    def __init__(self, *paths: str, values: _T.Union[_T.Mapping, _T.Callable[[], _T.Mapping]] = None, makedir: bool = True):
        self.basepaths = paths
        self.values = values
        self.makedir = makedir

    def __call__(self, *paths: str, makedir=None):
        path = join(*self.basepaths, *paths)
        path = format(path, self.values)
        if makedir is None:
            makedir = self.makedir
        if makedir:
            makedirs(path)
        return path

    def __str__(self):
        return self.basepaths

    def __repr__(self):
        return f"{self.__class__.__qualname__}(basepaths={self.basepaths!r}, values={self.values!r}, makedir={self.makedir})"


def __init_module():
    import sys

    current_module = sys.modules[__name__]
    OldModuleClass = current_module.__class__

    class NewModuleClass(OldModuleClass):
        def __call__(self, *paths: str, values: _T.Union[_T.Mapping, _T.Callable[[], _T.Mapping]] = None, makedir: bool = True):
            return Dirpath(*paths, values=values, makedir=makedir)
    current_module.__class__ = NewModuleClass


__init_module()
del __init_module
