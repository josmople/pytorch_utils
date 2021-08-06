import typing as _T
from string import Formatter


class DefaultStrFormatterArg:

    def __init__(self, key: str, conversion: str = None, format_spec: str = ""):
        self.key = key
        self.conversion = conversion
        self.format_spec = format_spec

    def __str__(self):
        k = str(self.key)
        c = "" if self.conversion is None else f"!{self.conversion}"
        f = "" if len(self.format_spec) == 0 else f":{self.format_spec}"
        return f"{{{k}{c}{f}}}"

    def __repr__(self):
        return f"DefaultStrFormatterArg(key='{self.key}', conversion='{self.conversion}', format_spec='{self.format_spec}')"


class DefaultStrFormatter(Formatter):
    def __init__(self, default_fn=str):
        self.default_fn = default_fn

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            try:
                return kwds[key]
            except KeyError:
                pass
            except IndexError:
                pass

        if isinstance(key, int):
            try:
                return args[key]
            except IndexError:
                pass
            except KeyError:
                pass

        return DefaultStrFormatterArg(key=key)

    def convert_field(self, obj, conversion):
        if isinstance(obj, DefaultStrFormatterArg):
            obj.conversion = conversion
            return obj
        return super().convert_field(obj, conversion)

    def format_field(self, obj, format_spec):
        if isinstance(obj, DefaultStrFormatterArg):
            obj.format_spec = format_spec
            return self.default_fn(obj)
        return super().format_field(obj, format_spec)


INSTANCE = DefaultStrFormatter()


def formatter(default_fn: _T.Callable[[DefaultStrFormatterArg], str] = None):
    if default_fn is None:
        formatter = INSTANCE
    else:
        formatter = DefaultStrFormatter(default_fn)
    return formatter


def default_format(format_string, /, *args, **kwargs):
    return INSTANCE.format(format_string, *args, **kwargs)


def default_vformat(format_string, args, kwargs):
    return INSTANCE.vformat(format_string, args, kwargs)


def __init_module():
    import sys

    current_module = sys.modules[__name__]
    OldModuleClass = current_module.__class__

    class NewModuleClass(OldModuleClass):
        def __call__(self, format_string, /, *args, **kwargs):
            return default_format(format_string, *args, **kwargs)
    current_module.__class__ = NewModuleClass


__init_module()
del __init_module
