class ContextValue:

    def vget(self, key):
        raise NotImplementedError()

    def vset(self, key, val):
        raise NotImplementedError()

    def vdel(self, key):
        raise NotImplementedError()


CONTEXT_CLASSES_CACHE = {}


def factory(data_key="Δ", allow_read=True, allow_write=True, allow_delete=True, access_item=True, access_attr=True, use_cval=False):
    name = f"Context_{data_key}"

    if allow_read or allow_write or allow_delete:
        name += "_"
        name += "R" if allow_read else ""
        name += "W" if allow_write else ""
        name += "D" if allow_delete else ""

    if access_item or access_item:
        name += "_"
        name += "I" if access_item else ""
        name += "A" if access_attr else ""

    if use_cval:
        name += "_C"

    if name in CONTEXT_CLASSES_CACHE:
        return CONTEXT_CLASSES_CACHE[name]

    if use_cval:
        def _read(self, key):
            data = object.__getattribute__(self, data_key)
            obj = data[key]
            if isinstance(obj, ContextValue):
                return obj.vget(key)
            return obj

        def _write(self, key, val):
            data = object.__getattribute__(self, data_key)
            if key in data:
                obj = data[key]
                if isinstance(obj, ContextValue):
                    obj.vset(key, val)
                    return
            data[key] = val

        def _delete(self, key):
            data = object.__getattribute__(self, data_key)
            if key in data:
                obj = data[key]
                if isinstance(obj, ContextValue):
                    obj.vdel(key)
                    return
            del data[key]

        def _call(self):
            data = object.__getattribute__(self, data_key)
            out = {}
            for key in data:
                out[key] = _read(self, key)
            return out
    else:
        def _read(self, key):
            data = object.__getattribute__(self, data_key)
            return data[key]

        def _write(self, key, val):
            data = object.__getattribute__(self, data_key)
            data[key] = val

        def _delete(self, key):
            data = object.__getattribute__(self, data_key)
            del data[key]

        def _call(self):
            data = object.__getattribute__(self, data_key)
            out = {}
            for key in data:
                out[key] = data[key]
            return out

    methods = {}

    def _init(self, _=None):
        object.__setattr__(self, data_key, _)

    def _iter(self):
        data = object.__getattribute__(self, data_key)
        return iter(data)

    def _str(self):
        return str(self())

    def _repr(self):
        return f"{self.__class__.__name__}({data_key}={self()})"

    methods["__init__"] = _init
    methods["__call__"] = _call
    methods["__iter__"] = _iter
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

    newcls = type(name, (), methods)

    CONTEXT_CLASSES_CACHE[name] = newcls
    return newcls
