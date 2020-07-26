class ContextNull:

    def __init__(self):
        raise Exception("This class is not meant to be instantiated")


class ContextValue:

    def vget(self, key):
        raise NotImplementedError()

    def vset(self, key, val):
        raise NotImplementedError()

    def vdel(self, key):
        raise NotImplementedError()


class ContextOperation:

    def __call__(self, ctx, data, params):
        pass


class Context:

    def __call__(self, key=ContextNull, val=ContextNull):
        pass

    def __iter__(self):
        pass

    def __contains__(self, obj):
        pass


CONTEXT_CLASSES_CACHE = {}


def factory(data_attr="Δ", default_key="__default__", allow_read=True, allow_write=True, allow_delete=True, access_item=True, access_attr=True, use_cval=False):
    allow = ""
    if allow_read or allow_write or allow_delete:
        allow += "R" if allow_read else ""
        allow += "W" if allow_write else ""
        allow += "D" if allow_delete else ""

    access = ""
    if access_item or access_item:
        access += "I" if access_item else ""
        access += "A" if access_attr else ""

    identifier = f"[data_attr={repr(data_attr)},default_key={repr(default_key)},allow={repr(allow)},access={repr(access)},cval={use_cval}]"

    if identifier in CONTEXT_CLASSES_CACHE:
        return CONTEXT_CLASSES_CACHE[identifier]

    if use_cval:
        def _read(self, key):
            if not allow_read:
                raise NotImplementedError("Cannot read data")

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
            if not allow_write:
                raise NotImplementedError("Cannot write data")

            data = object.__getattribute__(self, data_attr)
            if key in data:
                obj = data[key]
                if isinstance(obj, ContextValue):
                    obj.vset(key, val)
                    return
            data[key] = val

        def _delete(self, key):
            if not allow_delete:
                raise NotImplementedError("Cannot delete data")

            data = object.__getattribute__(self, data_attr)
            if key in data:
                obj = data[key]
                if isinstance(obj, ContextValue):
                    obj.vdel(key)
                    return
            del data[key]
    else:
        def _read(self, key):
            if not allow_read:
                raise NotImplementedError("Cannot read data")

            data = object.__getattribute__(self, data_attr)

            if key in data:
                obj = data[key]
            elif default_key in data:
                obj = data[default_key]
            else:
                obj = data[key]  # Attempt to raise an error

            return obj

        def _write(self, key, val):
            if not allow_write:
                raise NotImplementedError("Cannot write data")

            data = object.__getattribute__(self, data_attr)
            data[key] = val

        def _delete(self, key):
            if not allow_delete:
                raise NotImplementedError("Cannot delete data")

            data = object.__getattribute__(self, data_attr)
            del data[key]

    access_methods = {}

    if allow_read:
        if access_item:
            access_methods["__getitem__"] = _read
        if access_attr:
            access_methods["__getattr__"] = _read

    if allow_write:
        if access_item:
            access_methods["__setitem__"] = _write
        if access_attr:
            access_methods["__setattr__"] = _write

    if allow_delete:
        if access_item:
            access_methods["__delitem__"] = _delete
        if access_attr:
            access_methods["__delattr__"] = _delete

    ContextAccessor = type(f"ContextAccessor{identifier}", (), access_methods)

    class ContextDerived(ContextAccessor, Context):

        def __init__(self, _=None):
            object.__setattr__(self, data_attr, _ or {})

        def __call__(self, key=ContextNull, val=ContextNull):
            key_null = key is ContextNull
            val_null = val is ContextNull

            if key_null and val_null:  # Do EVAL
                data = object.__getattribute__(self, data_attr)
                out = {}
                for key in data:
                    out[key] = _read(self, key)
                return out

            if isinstance(key, ContextOperation):
                return key(self, object.__getattribute__(self, data_attr), val)

            if not key_null and val_null:  # Do GET
                return _read(self, key, val)
            if not key_null and not val_null:  # Do SET
                return _write(self, key, val)

            if key_null and not val_null:  # Do DEFAULT
                return _write(self, default_key, val)

        def __invert__(self):
            return object.__getattribute__(self, data_attr)

        def __neg__(self):
            return {
                "data_attr": data_attr,
                "default_key": default_key,
                "allow_read": allow_read,
                "allow_write": allow_write,
                "allow_delete": allow_delete,
                "allow_code": allow,
                "access_item": access_item,
                "access_attr": access_attr,
                "access_code": access,
                "use_cval": use_cval
            }

        def __iter__(self):
            data = object.__getattribute__(self, data_attr)
            return iter(data)

        def __contains__(self, key):
            data = object.__getattribute__(self, data_attr)
            return val in data

        def __str__(self):
            return str(self())

        def __repr__(self):
            return f"{self.__class__.__name__}({data_attr}={repr(~self)})"

    ContextDerived.__name__ = f"Context{identifier}"
    ContextDerived.__qualname__ = f"Context{identifier}"
    CONTEXT_CLASSES_CACHE[identifier] = ContextDerived
    return ContextDerived
