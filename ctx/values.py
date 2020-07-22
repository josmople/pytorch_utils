from .context import ContextValue


class LambdaValue(ContextValue):

    @staticmethod
    def _getter_unallowed(key):
        raise Exception(f"getter for {k} is undefined")

    @staticmethod
    def _setter_unallowed(key, val):
        raise Exception(f"setter for {k} is undefined")

    @staticmethod
    def _deleter_unallowed(key):
        raise Exception(f"deleter for {k} is undefined")

    def __init__(self, getter=None, setter=None, deleter=None):
        self.getter = getter or self._getter_unallowed
        self.setter = setter or self._setter_unallowed
        self.deleter = deleter or self._deleter_unallowed

    def vget(self, key):
        return self.getter(key)

    def vset(self, key, val):
        return self.setter(key, val)

    def vdel(self, key):
        return self.deleter(key)

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}(getter={self.getter}, setter={self.setter}, deleter={self.deleter})"


class ProxyAttrValue(ContextValue):

    def __init__(self, obj, key, allow_read=True, allow_write=True, allow_delete=True):
        self.obj = obj
        self.key = key
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.allow_delete = allow_delete

    def vget(self, key):
        if self.allow_read:
            return getattr(self.obj, self.key)
        raise Exception(f"Reading db[{self.key}] is not allowed")

    def vset(self, key, val):
        if self.allow_write:
            setattr(self.obj, self.key, val)
        raise Exception(f"Writing db[{self.key}] is not allowed")

    def vdel(self, key):
        if self.allow_delete:
            delattr(self.obj, self.key)
        raise Exception(f"Deleting db[{self.key}] is not allowed")

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        access = f"{int(self.allow_read)}{int(self.allow_write)}{int(self.allow_delete)}"
        return f"{self.__class__.__name__}(key={repr(self.key)},access={access})"


class ProxyItemValue(ContextValue):

    def __init__(self, obj, key, allow_read=True, allow_write=True, allow_delete=True):
        self.obj = obj
        self.key = key
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.allow_delete = allow_delete

    def vget(self, key):
        if self.allow_read:
            return self.obj[self.key]
        raise Exception(f"Reading db[{self.key}] is not allowed")

    def vset(self, key, val):
        if self.allow_write:
            self.obj[self.key] = val
        raise Exception(f"Writing db[{self.key}] is not allowed")

    def vdel(self, key):
        if self.allow_delete:
            del self.obj[self.key]
        raise Exception(f"Deleting db[{self.key}] is not allowed")

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        access = f"{int(self.allow_read)}{int(self.allow_write)}{int(self.allow_delete)}"
        return f"{self.__class__.__name__}(key={repr(self.key)},access={access})"


class GlobalValue(ProxyItemValue):

    def __init__(self, key, allow_read=True, allow_write=True, allow_delete=True, stack_idx=1):
        from inspect import stack
        db = stack()[stack_idx][0].f_globals
        super().__init__(obj=db, key=key, allow_read=allow_read, allow_write=allow_write, allow_delete=allow_delete)

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        access = f"{int(self.allow_read)}{int(self.allow_write)}{int(self.allow_delete)}"
        return f"{self.__class__.__name__}(key={repr(self.key)},access={access})"


class ConstValue(ContextValue):

    def __init__(self, val):
        self.val = val

    def vget(self, key):
        return self.val

    def vset(self, key, val):
        raise Exception(f"Cannot overwrite constant: {self.val}")

    def vdel(self, key):
        raise Exception(f"Cannot delete constant: {self.val}")

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f"{self.__class__.__name__}(val={repr(self.val)})"
