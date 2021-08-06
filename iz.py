from __future__ import annotations
import typing as T


class iztype:  # Class flag
    def __eq__(self, other): raise NotImplementedError()


class anytype(iztype):
    def __eq__(self, other): return True
    def __getattr__(self, key): return self
    def __str__(self): return "ANY"
    def __repr__(self): return "anytype.ANY"


class logicaltype(iztype):

    def __init__(self, *objs, equal=True):
        self.objs = objs
        self.equal = equal

    def eqops(self, other): raise NotImplementedError()

    def __eq__(self, other):
        if self.equal:
            return self.eqops(other)
        return not self.eqops(other)

    def __str__(self): return repr(self.objs)
    def __repr__(self): return f"{self.__class__.__name__}({', '.join([repr(obj) for obj in self.objs])})"


class andtype(logicaltype):

    def eqops(self, other):
        for obj in self.objs:
            if obj != other:
                return False
        return True


class ortype(logicaltype):

    def eqops(self, other):
        for obj in self.objs:
            if obj == other:
                return True
        return False


class memtype(iztype):

    def __init__(self, value: object = None, empty: bool = False, equal: bool = True):
        self.value: object = value
        self.empty: bool = empty
        self.equal: bool = equal

    def __str__(self): return repr(self.value)
    def __repr__(self): return f"memtype(value={self.value!r}, empty={self.empty}, equal={self.equal})"

    def _extract_value(self, other):
        assert not self.empty
        if isinstance(other, memtype):
            assert not other.empty
            assert self.equal == other.equal
            other = other.value
        return other

    def __eq__(self, other):
        if self.empty:
            self.value = other
            self.empty = False
            return True
        if self.equal:
            return self.value == other
        return self.value != other

    def __invert__(self):
        return memtype(self.value, self.empty, not self.equal)

    def __add__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value + other_val, empty=False, equal=self.equal)

    def __radd__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val + self.value, empty=False, equal=self.equal)

    def __sub__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value - other_val, empty=False, equal=self.equal)

    def __rsub__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val - self.value, empty=False, equal=self.equal)

    def __mul__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value * other_val, empty=False, equal=self.equal)

    def __rmul__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val * self.value, empty=False, equal=self.equal)

    def __pow__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value ** other_val, empty=False, equal=self.equal)

    def __rpow__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val ** self.value, empty=False, equal=self.equal)

    def __mod__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value % other_val, empty=False, equal=self.equal)

    def __rmod__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val % self.value, empty=False, equal=self.equal)

    def __truediv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value.__truediv__(other_val), empty=False, equal=self.equal)

    def __rtruediv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val.__truediv__(self.value), empty=False, equal=self.equal)

    def __floordiv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value // other_val, empty=False, equal=self.equal)

    def __rfloordiv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val // self.value, empty=False, equal=self.equal)

    def __and__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return andtype(self.value, other_val, equal=self.equal)

    def __rand__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return andtype(other_val, self.value, equal=self.equal)

    def __or__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return ortype(self.value, other_val, equal=self.equal)

    def __ror__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return ortype(other_val, self.value, equal=self.equal)


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

    def __getattr__(self, key) -> memtype:
        if key not in self._data or self._override:
            self._data[key] = memtype(value=None, empty=True, equal=True)
        return self._data[key]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class __remote_locals:

    def __init__(self, _stackidx):
        self._stackidx = _stackidx

    @property
    def _caller_locals(self):
        from sys import _getframe
        frame = _getframe(self._stackidx)
        return frame.f_locals

    def __getitem__(self, key):
        return self._caller_locals[key]

    def __setitem__(self, key, val):
        self._caller_locals[key] = val

    def __delitem__(self, key):
        del self._caller_locals[key]

    def __contains__(self, key):
        return key in self._caller_locals


ANY = anytype()
NEW = ctx(__remote_locals(3), _override=True)


def __init_module():
    import sys

    current_module = sys.modules[__name__]
    OldModuleClass = current_module.__class__

    class NewModuleClass(ctx, OldModuleClass):
        ...
    current_module.__class__ = NewModuleClass
    ctx.__init__(current_module, _data=__remote_locals(4), _override=False)


__init_module()
del __init_module
