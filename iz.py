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


class ctx(dict):
    ANY: anytype

    def __getattr__(self, key) -> eq_mem:
        if key not in self:
            self[key] = eq_mem(val=None, empty=True)
        return self[key]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


ANY = ctx.ANY = anytype()


def __init_module():
    import sys
    current_module = sys.modules[__name__]

    OldModuleClass = current_module.__class__

    class NewModuleClass(OldModuleClass):
        def __getattr__(self, key):
            import inspect
            locals = inspect.currentframe().f_back.f_back.f_locals
            if key not in locals:
                locals[key] = eq_mem(val=None, empty=True)
            val = locals[key]
            assert isinstance(val, iztype), f"The name '{key}' is used already in the local scope"
            return val

    current_module.__class__ = NewModuleClass

    del current_module.__init_module


__init_module()
