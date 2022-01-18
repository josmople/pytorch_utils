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


def tag(name, directory: str = None, params: dict = None, desc: str = None, delete_similar=False, ext="tag.metadata"):
    if directory is None:
        directory = ""
    if callable(directory):
        directory = directory()
    directory = str(directory)

    if delete_similar:
        from glob import glob
        from os.path import join
        from os import remove
        hits = glob(join(directory, f"{name}*.{ext}"))
        for hit in hits:
            remove(hit)

    if params is None:
        params_text = ""
    else:
        import re
        WHITESPACE_FINDER = re.compile(r"\s+")

        params_text = ""
        for k, v in params.items():
            v = WHITESPACE_FINDER.sub(" ", str(v)).strip()  # Replace any whitespace with single space
            params_text += f"{k}={v}"
        params_text = f"({params_text})"

    from os.path import join
    filename = join(directory, f"{name}{params_text}.{ext}")

    with open(filename, "w+") as f:
        if desc is not None:
            f.write(str(desc))

    return filename


__init_module()
del __init_module
