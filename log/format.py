from string import Formatter as _Formatter


class DefaultStrFormatter(_Formatter):
    def __init__(self, default_fn=lambda k: f"{{{k}}}"):
        self.default_fn = default_fn

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            if key in kwds:
                return kwds[key]

        if isinstance(key, int):
            if key in range(0, len(args)):
                return args[key]

        return self.default_fn(key)


instance = DefaultStrFormatter(default_fn=lambda k: f"{{{k}}}")


def get_formatter(default_fn=None):
    if default_fn is None:
        formatter = instance
    else:
        formatter = DefaultStrFormatter(default_fn)
    return formatter


def format(text, *args, default_fn=None, **kwds):
    return get_formatter(default_fn).format(text, *args, **kwds)


def vformat(text, args, kwds, default_fn=None):
    return get_formatter(default_fn).vformat(text, args, kwds)


def mformat(text, values, default_fn=None):
    return get_formatter(default_fn).vformat(text, values, values)


del _Formatter
