from string import Formatter as _Formatter
from collections.abc import Mapping as _Mapping


class _DefaultStrFormatter(_Formatter):
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


_formatter = _DefaultStrFormatter(default_fn=lambda k: f"{{{k}}}")


def default_format_string(text, vals):
    return _formatter.vformat(text, [], vals)


def no_operation(*args, **kwds):
    return None



class ContextModel:

    data = None
    default = None
    formatter = None


class ContextProperty:

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __str__(self):
        return str(self.getter())

    def __repr__(self):
        return f"ContextProperty(getter={self.getter}, setter={self.setter})"


class Context:

    ι = ""  # Internal

    def __init__(self, DEFAULT=no_operation, FORMAT=default_format_string, **kwds):
        object.__setattr__(self, "ι", ContextModel())
        self.ι.data = kwds
        self.ι.default = DEFAULT
        self.ι.formatter = FORMAT

    def __invert__(self):
        data = self.ι.data
        out = {}
        for k in data:
            v = self[k]
            if isinstance(v, Context):
                v = ~v
            out[k] = v
        return out

    def __len__(self):
        data = self.ι.data
        return len(data)

    def __getitem__(self, k):
        data = self.ι.data

        if k not in data:
            fn = self.ι.default
            self[k] = fn(k)

        v = data[k]

        if isinstance(v, ContextProperty):
            return v.getter()
        return v

    def __setitem__(self, k, v):
        data = self.ι.data

        if isinstance(v, ContextProperty):
            data[k] = v
            return

        if k in data:
            ov = data[k]
            if isinstance(ov, ContextProperty):
                ov.setter(v)
                return

        data[k] = v

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v

    def __delitem__(self, v):
        data = self.ι.data
        del data[v]

    def __contains__(self, k):
        data = self.ι.data
        return k in data

    def __iter__(self):
        data = self.ι.data
        return iter(data)

    def __str__(self):
        data = self.ι.data
        return str(data)

    def __repr__(self):
        data = self.ι.data
        default = self.ι.default
        formatter = self.ι.formatter
        return f"Context(data={repr(data)}, default={repr(default)}, formatter={repr(formatter)})"

    def __rmatmul__(self, text):
        assert isinstance(text, str)
        formatter = self.ι.formatter
        return formatter(text, self)

    def __call__(self, getter=None, setter=None):
        if getter is None and setter is None:
            return ~self

        if isinstance(getter, str):
            formatter = self.ι.formatter
            return formatter(text, self)

        getter = getter or no_operation
        setter = setter or no_operation

        assert callable(getter)
        assert callable(setter)

        return ContextProperty(getter, setter)


def get_data(context):
    return context.ι.data


def set_data(context, data):
    context.ι.data = data


def get_default(context):
    return context.ι.default


def set_default(context, fn):
    fn = fn or no_operation
    assert callable(fn)
    context.ι.default = fn


def get_formatter(context):
    return context.ι.formatter


def set_formatter(context, fn):
    fn = fn or no_operation
    assert callable(fn)
   context.ι.defauformatterlt = fn
