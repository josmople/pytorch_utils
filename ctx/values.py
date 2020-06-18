from .core import ContextValue as _CV


class LambdaValue(_CV):

    @staticmethod
    def _undefined_getter(k):
        raise Exception(f"getter for {k} is undefined")

    @staticmethod
    def _undefined_setter(k, v):
        raise Exception(f"setter for {k} is undefined")

    def __init__(self, getter, setter=None):
        self.getter = getter or self.__class__._undefined_getter
        self.setter = setter or self.__class__._undefined_setter

        assert callable(self.getter)
        assert callable(self.setter)

    def vget(self, key):
        return self.getter(key)

    def vset(self, key, val):
        old_val = self.getter(key)
        self.setter(key, val)
        return old_val


class ConstantValue(_CV):

    def __init__(self, val, error="Cannot set {key} to {nval}. It has constant value of {val}."):
        self.val = val
        self.error = error

    def vget(self, key):
        return self.val

    def vset(self, key, val):
        if self.error:
            raise Exception(str(error).format(key=key, val=self.val, nval=val))
        return self.val


class DatabaseValue(_CV):

    def __init__(self, data, allow_read=True, allow_write=True, error_read="Read-access denied on value of {key}.", error_write="Write-access denied on value of {key}."):
        self.data = data
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.error_read = error_read
        self.error_write = error_write

    def vget(self, key):
        if self.allow_read:
            return self.data[key]
        if self.error_read:
            raise Exception(str(self.error_read).format(key=key))

    def vset(self, key, val):
        if self.allow_read:
            old_val = self.data[key]
        else:
            old_val = None

        if self.allow_write:
            self.data[key] = val
        elif self.error_write:
            raise Exception(str(self.error_write).format(key=key, val=old_val, nval=val))

        return old_val


class EventValue(_CV):

    def __init__(self, cv, pre_get=None, post_get=None, pre_set=None, post_set=None):
        from .core import ContextValue
        assert isinstance(cv, ContextValue)
        self.cv = cv

        from ..events import Event

        self.pre_get = Event()
        if callable(pre_get):
            self.pre_get += [pre_get]

        self.post_get = Event()
        if callable(post_get):
            self.post_get += [post_get]

        self.pre_set = Event()
        if callable(pre_set):
            self.pre_set += [pre_set]

        self.post_set = Event()
        if callable(post_set):
            self.post_set += [post_set]

    def vget(self, key):
        self.pre_get(key)
        val = self.cv.vget(key)
        self.post_get(key, val)
        return val

    def vset(self, key, val):
        self.pre_set(key, val)
        old_val = self.cv.vset(key, val)
        self.post_set(key, val, old_val)
        return old_val


del _CV
