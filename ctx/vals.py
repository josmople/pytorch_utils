from .context import ContextValue


class LambdaValue(ContextValue):

    def undefined_getter(self, ctx, data, key):
        raise Exception(f"getter for {k} is undefined")

    def undefined_setter(self, ctx, data, key, val):
        raise Exception(f"setter for {k} is undefined")

    def undefined_deleter(self, ctx, data, key):
        raise Exception(f"deleter for {k} is undefined")

    def __init__(self, getter=None, setter=None, deleter=None):
        self.getter = getter
        self.setter = setter
        self.deleter = deleter

    def vget(self, ctx, data, key):
        if self.getter is None:
            return self.undefined_getter(ctx, data, key)
        return self.getter(key)

    def vset(self, ctx, data, key, val):
        if self.setter is None:
            return self.undefined_setter(ctx, data, key, val)
        return self.setter(key, val)

    def vdel(self, ctx, data, key):
        if self.deleter is None:
            return self.undefined_deleter(ctx, data, key)
        return self.deleter(key)

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}(getter={self.getter}, setter={self.setter}, deleter={self.deleter})"


class ProxyAttrValue(ContextValue):

    def __init__(self, db, key=None, allow_read=True, allow_write=True, allow_delete=True):
        self.db = db
        self.key = key
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.allow_delete = allow_delete

    def vget(self, ctx, data, key):
        if self.allow_read:
            return getattr(self.db, self.key or key)
        raise Exception(f"Reading db[{self.key}] is not allowed")

    def vset(self, ctx, data, key, val):
        if self.allow_write:
            setattr(self.db, self.key or key, val)
        raise Exception(f"Writing db[{self.key}] is not allowed")

    def vdel(self, ctx, data, key):
        if self.allow_delete:
            delattr(self.db, self.key or key)
        raise Exception(f"Deleting db[{self.key}] is not allowed")

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        access = f"{int(self.allow_read)}{int(self.allow_write)}{int(self.allow_delete)}"
        return f"{self.__class__.__name__}(key={repr(self.key)},access={access})"


class ProxyItemValue(ContextValue):

    def __init__(self, db, key=None, allow_read=True, allow_write=True, allow_delete=True):
        self.db = db
        self.key = key
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.allow_delete = allow_delete

    def vget(self, ctx, data, key):
        if self.allow_read:
            return self.db[self.key or key]
        raise Exception(f"Reading db[{self.key}] is not allowed")

    def vset(self, ctx, data, key, val):
        if self.allow_write:
            self.db[self.key or key] = val
        raise Exception(f"Writing db[{self.key}] is not allowed")

    def vdel(self, ctx, data, key):
        if self.allow_delete:
            del self.db[self.key or key]
        raise Exception(f"Deleting db[{self.key}] is not allowed")

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        access = f"{int(self.allow_read)}{int(self.allow_write)}{int(self.allow_delete)}"
        return f"{self.__class__.__name__}(key={repr(self.key)},access={access})"


class GlobalValue(ProxyItemValue):

    def __init__(self, ctx, data, key=None, allow_read=True, allow_write=True, allow_delete=True, stack_idx=1):
        from inspect import stack
        db = stack()[stack_idx][0].f_globals
        super().__init__(db=db, key=key, allow_read=allow_read, allow_write=allow_write, allow_delete=allow_delete)

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        access = f"{int(self.allow_read)}{int(self.allow_write)}{int(self.allow_delete)}"
        return f"{self.__class__.__name__}(key={repr(self.key)},access={access})"


class ConstValue(ContextValue):

    def __init__(self, val):
        self.val = val

    def vget(self, ctx, data, key):
        return self.val

    def vset(self, ctx, data, key, val):
        raise Exception(f"Cannot overwrite constant: {self.val}")

    def vdel(self, ctx, data, key):
        raise Exception(f"Cannot delete constant: {self.val}")

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f"{self.__class__.__name__}(val={repr(self.val)})"


class FileValue(ContextValue):

    def undefined_read(self, ctx, data, key):
        raise Exception(f"Cannot read file {key}: file='{self.path}'")

    def undefined_write(self, ctx, data, key, val):
        raise Exception(f"Cannot write file {key}: file='{self.path}'")

    def undefined_remove(self, ctx, data, key):
        raise Exception(f"Cannot delete file {key}: file='{self.path}'")

    def __init__(self, path, read=None, write=None, remove=None, autocreate=False):
        self.path = path
        self.read = read
        self.write = write
        self.remove = remove

        from os.path import exists
        if not exists(path):
            if callable(autocreate):
                autocreate(path)
            elif autocreate:
                open(path, "x").close()

    def vget(self, ctx, data, key):
        if self.read is None:
            return self.undefined_read(ctx, data, key)
        return self.read(self.path)

    def vset(self, ctx, data, key, val):
        if self.write is None:
            return self.undefined_write(ctx, data, key)
        return self.write(self.path, val)

    def vdel(self, ctx, data, key):
        if self.remove is None:
            return self.undefined_remove(ctx, data, key)
        return self.remove(self.path)

    def do_read(self):
        return self.read(self.path)

    def do_write(self, val):
        return self.write(self.path, val)

    def do_remove(self):
        return self.remove(self.path)

    def exists(self):
        from os.path import exists
        return exists(self.path)

    def openfile(self, mode="w+", **kwds):
        return open(self.path, mode, **kwds)
