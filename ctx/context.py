class ContextValue:

    def vget(self, key):
        raise NotImplementedError()

    def vset(self, key, val):
        raise NotImplementedError()

    def vdel(self, key):
        raise NotImplementedError()


class Context:

    def __init__(self):
        pass

    def __call__(self):
        pass

    def __iter__(self):
        pass

    def __contains__(self):
        pass


CONTEXT_CLASSES_CACHE = {}


def factory(data_attr="Δ", default_key="__default__", allow_read=True, allow_write=True, allow_delete=True, access_item=True, access_attr=True, use_cval=False):
    name = f"Context@{data_attr}@{default_key}"

    if allow_read or allow_write or allow_delete:
        name += "@"
        name += "R" if allow_read else ""
        name += "W" if allow_write else ""
        name += "D" if allow_delete else ""

    if access_item or access_item:
        name += "@"
        name += "I" if access_item else ""
        name += "A" if access_attr else ""

    if use_cval:
        name += "@C"

    if name in CONTEXT_CLASSES_CACHE:
        return CONTEXT_CLASSES_CACHE[name]

    if use_cval:
        def _read(self, key):
            data = object.__getattribute__(self, data_attr)

            if key in data:
                obj = data[key]
            elif default_key in data:
                obj = data[default_key]
            else:
                obj = data[key]  # Attempt to raise an error

            if isinstance(obj, ContextValue):
                return obj.vget(key)
            return obj

        def _write(self, key, val):
            data = object.__getattribute__(self, data_attr)
            if key in data:
                obj = data[key]
                if isinstance(obj, ContextValue):
                    obj.vset(key, val)
                    return
            data[key] = val

        def _delete(self, key):
            data = object.__getattribute__(self, data_attr)
            if key in data:
                obj = data[key]
                if isinstance(obj, ContextValue):
                    obj.vdel(key)
                    return
            del data[key]

        def _call(self):
            data = object.__getattribute__(self, data_attr)
            out = {}
            for key in data:
                out[key] = _read(self, key)
            return out
    else:
        def _read(self, key):
            data = object.__getattribute__(self, data_attr)

            if key in data:
                obj = data[key]
            elif default_key in data:
                obj = data[default_key]
            else:
                obj = data[key]  # Attempt to raise an error

            return obj

        def _write(self, key, val):
            data = object.__getattribute__(self, data_attr)
            data[key] = val

        def _delete(self, key):
            data = object.__getattribute__(self, data_attr)
            del data[key]

        def _call(self):
            data = object.__getattribute__(self, data_attr)
            out = {}
            for key in data:
                out[key] = data[key]
            return out

    methods = {}

    def _init(self, _=None):
        object.__setattr__(self, data_attr, _)

    def _iter(self):
        data = object.__getattribute__(self, data_attr)
        return iter(data)

    def _contains(self, val):
        data = object.__getattribute__(self, data_attr)
        return val in data

    def _str(self):
        return str(self())

    def _repr(self):
        return f"{self.__class__.__name__}({data_attr}={self()})"

    methods["__init__"] = _init
    methods["__call__"] = _call
    methods["__iter__"] = _iter
    methods["__contains__"] = _contains
    methods["__str__"] = _str
    methods["__repr__"] = _repr

    if allow_read:
        if access_item:
            methods["__getitem__"] = _read
        if access_attr:
            methods["__getattr__"] = _read

    if allow_write:
        if access_item:
            methods["__setitem__"] = _write
        if access_attr:
            methods["__setattr__"] = _write

    if allow_delete:
        if access_item:
            methods["__delitem__"] = _delete
        if access_attr:
            methods["__delattr__"] = _delete

    newcls = type(name, (Context,), methods)

    CONTEXT_CLASSES_CACHE[name] = newcls
    return newcls
