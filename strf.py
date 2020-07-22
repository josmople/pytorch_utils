from string import Formatter as _Formatter


class DefaultStrFormatterArg:

    def __init__(self, key, conversion=None, format_spec=""):
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


class DefaultStrFormatter(_Formatter):
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


_instance = DefaultStrFormatter()


def get_formatter(default_fn=None):
    if default_fn is None:
        formatter = _instance
    else:
        formatter = DefaultStrFormatter(default_fn)
    return formatter


def format(text, *args, default_fn=None, **kwds):
    return get_formatter(default_fn).format(text, *args, **kwds)


def vformat(text, args=None, kwds=None, default_fn=None):
    return get_formatter(default_fn).vformat(text, args or [], kwds or {})


def mformat(text, values, default_fn=None):
    return get_formatter(default_fn).vformat(text, values, values)


del _Formatter
