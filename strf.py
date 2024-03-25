import typing as _T
from string import Formatter


class DefaultStrFormatter(Formatter):

    class Args:
        def __init__(self, key: object, conversion: str | None = None, format_spec: str = ""):
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

    def __init__(self, default_fn: _T.Callable[[Args], str] = str):
        self.default_fn = default_fn

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            try:
                return kwds[key]
            except (KeyError, IndexError):
                pass

        if isinstance(key, int):
            try:
                return args[key]
            except (IndexError, KeyError):
                pass

        return self.Args(key=key)

    def convert_field(self, obj, conversion):
        if isinstance(obj, self.Args):
            obj.conversion = conversion
            return obj
        return super().convert_field(obj, conversion)

    def format_field(self, obj, format_spec):
        if isinstance(obj, self.Args):
            obj.format_spec = format_spec
            return self.default_fn(obj)
        return super().format_field(obj, format_spec)


DEFAULT_INSTANCE = DefaultStrFormatter()


def default_format(format_string, /, *args, **kwargs):
    return DEFAULT_INSTANCE.format(format_string, *args, **kwargs)


def default_vformat(format_string, args, kwargs):
    return DEFAULT_INSTANCE.vformat(format_string, args, kwargs)
