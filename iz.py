from __future__ import annotations
import typing as T

# TODO add support for or, and, xor operators


class iztype:  # Class flag
    pass


class anytype(iztype):
    def __getattr__(self, key):
        return self

    def __eq__(self, other):
        return True

    def __str__(self):
        return "ANY"

    def __repr__(self):
        return "ANY"


class memtype(iztype):

    def __init__(self, val=None, empty=True):
        self.val = val
        self.empty = empty

    def __str__(self):
        return "" if self.empty else repr(self.val)

    def __repr__(self):
        kv = [f"{k}={v!r}" for k, v in self.__dict__.items()]
        return f"{self.__class__.__name__}({','.join(kv)})"


class eq_mem(memtype):

    def __eq__(self, other):
        if self.empty:
            self.val = other
            self.empty = False
            return True
        return self.val == other

    def __invert__(self):
        return neq_mem(self.val, self.empty)

    def __add__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val + other_val)

    def __radd__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val + self.val)

    def __sub__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val - other_val)

    def __rsub__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val - self.val)

    def __mul__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val * other_val)

    def __rmul__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val * self.val)

    def __pow__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val ** other_val)

    def __rpow__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val ** self.val)

    def __mod__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val % other_val)

    def __rmod__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val % self.val)

    def __truediv__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val.__truediv__(other_val))

    def __rtruediv__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val.__truediv__(self.val))

    def __floordiv__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(self.val // other_val)

    def __rfloordiv__(self, other) -> eq_mem:
        assert not self.empty
        assert not isinstance(other, neq_mem)
        other_val = other.val if isinstance(other, eq_mem) else other
        return self.__class__(other_val // self.val)


class neq_mem(memtype):

    def __eq__(self, other):
        if self.empty:
            self.val = other
            self.empty = False
            return True
        return self.val != other

    def __invert__(self):
        return eq_mem(self.val, self.empty)

    def __add__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val + other_val)

    def __radd__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val + self.val)

    def __sub__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val - other_val)

    def __rsub__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val - self.val)

    def __mul__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val * other_val)

    def __rmul__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val * self.val)

    def __pow__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val ** other_val)

    def __rpow__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val ** self.val)

    def __mod__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val % other_val)

    def __rmod__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val % self.val)

    def __truediv__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val.__truediv__(other_val))

    def __rtruediv__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val.__truediv__(self.val))

    def __floordiv__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(self.val // other_val)

    def __rfloordiv__(self, other) -> neq_mem:
        assert not self.empty
        assert not isinstance(other, eq_mem)
        other_val = other.val if isinstance(other, neq_mem) else other
        return self.__class__(other_val // self.val)


class ctx:

    def __init__(self, _data=None, _override=False):
        self._data = _data or {}
        self._override = _override

    @property
    def ANY(self):
        return ANY

    @property
    def NEW(self):
        return ctx(_data=self._data, _override=True)

    def __getattr__(self, key) -> eq_mem:
        if key not in self._data or self._override:
            self._data[key] = eq_mem(val=None, empty=True)
        return self._data[key]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class __remote_locals:

    def __init__(self, stack_idx):
        self.stack_idx = stack_idx

    @property
    def data(self):
        from sys import _getframe
        frame = _getframe(self.stack_idx)
        return frame.f_locals

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, key):
        return key in self.data


ANY = anytype()
NEW = ctx(__remote_locals(3), _override=True)


def __init_module():
    import sys
    current_module = sys.modules[__name__]

    OldModuleClass = current_module.__class__

    CTX = ctx(__remote_locals(5), _override=False)

    class NewModuleClass(OldModuleClass):
        def __getattr__(self, key):
            return getattr(CTX, key)

    current_module.__class__ = NewModuleClass

    del current_module.__init_module


__init_module()
