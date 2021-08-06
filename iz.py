from __future__ import annotations
import typing as T


class iztype:  # Class flag
    def __eq__(self, other): raise NotImplementedError()


class anytype(iztype):
    def __eq__(self, other): return True
    def __getattr__(self, key): return self
    def __str__(self): return "ANY"
    def __repr__(self): return "anytype.ANY"


class invertabletype(iztype):

    def __init__(self, pos=True) -> None:
        self.pos = pos

    def equals(self, other): raise NotImplementedError()

    def __invert__(self):
        from copy import deepcopy
        dup = deepcopy(self)
        dup.pos = not dup.pos
        return dup

    def __eq__(self, other):
        if self.pos:
            return self.equals(other)
        return not self.equals(other)


class logicaltype(invertabletype):

    def __init__(self, *comps: object, pos: bool = True):
        super().__init__(pos=pos)
        self.comps = comps

    def __str__(self): return repr(self.comps)
    def __repr__(self): return f"{self.__class__.__name__}({', '.join([repr(obj) for obj in self.comps])})"


class andtype(logicaltype):

    def equals(self, other):
        for comp in self.comps:
            if comp != other:
                return False
        return True


class ortype(logicaltype):

    def equals(self, other):
        for comp in self.comps:
            if comp == other:
                return True
        return False


class memtype(invertabletype):

    def __init__(self, value: object = None, empty: bool = False, pos: bool = True):
        invertabletype.__init__(self, pos=pos)
        self.value: object = value
        self.empty: bool = empty

    def __str__(self): return repr(self.value)
    def __repr__(self): return f"memtype(value={self.value!r}, empty={self.empty}, equal={self.pos})"

    def equals(self, other):
        if self.empty:
            assert self.pos, "Initialization of value must be done in a positive context"
            self.value = other
            self.empty = False
            return True
        return self.value == other

    def _extract_value(self, other):
        assert not self.empty
        if isinstance(other, memtype):
            assert not other.empty
            assert self.pos == other.pos
            other = other.value
        return other

    def __add__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value + other_val, empty=False, pos=self.pos)

    def __radd__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val + self.value, empty=False, pos=self.pos)

    def __sub__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value - other_val, empty=False, pos=self.pos)

    def __rsub__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val - self.value, empty=False, pos=self.pos)

    def __mul__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value * other_val, empty=False, pos=self.pos)

    def __rmul__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val * self.value, empty=False, pos=self.pos)

    def __pow__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value ** other_val, empty=False, pos=self.pos)

    def __rpow__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val ** self.value, empty=False, pos=self.pos)

    def __mod__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value % other_val, empty=False, pos=self.pos)

    def __rmod__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val % self.value, empty=False, pos=self.pos)

    def __truediv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value.__truediv__(other_val), empty=False, pos=self.pos)

    def __rtruediv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val.__truediv__(self.value), empty=False, pos=self.pos)

    def __floordiv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(self.value // other_val, empty=False, pos=self.pos)

    def __rfloordiv__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return memtype(other_val // self.value, empty=False, pos=self.pos)

    def __and__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return andtype(self.value, other_val, pos=self.pos)

    def __rand__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return andtype(other_val, self.value, pos=self.pos)

    def __or__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return ortype(self.value, other_val, pos=self.pos)

    def __ror__(self, other) -> memtype:
        other_val = self._extract_value(other)
        return ortype(other_val, self.value, pos=self.pos)


class ctx:

    def __init__(self, _data: T.MutableMapping = None, _override: bool = False, _pos: bool = True, _isroot=True):
        self._data: T.MutableMapping = _data or {}
        self._override: bool = _override
        self._pos: bool = _pos
        self._isroot: bool = _isroot

    @property
    def ANY(self):
        return ANY

    @property
    def NEW(self):
        assert self._isroot, "This functionality can only be access by root 'ctx'"
        return ctx(_data=self._data, _override=True, _pos=self._pos, _isroot=False)

    @property
    def NOT(self):
        return ctx(_data=self._data, _override=self._override, _pos=not self._pos, _isroot=False)

    def __getattr__(self, key) -> memtype:
        if key not in self._data or self._override:
            self._data[key] = memtype(value=None, empty=True, pos=self._pos)
        return self._data[key]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class __remote_locals:

    def __init__(self, _stackidx):
        self._stackidx = _stackidx

    # @property
    # def _caller_locals(self):
    #     from sys import _getframe
    #     frame = _getframe(self._stackidx)

    #     import inspect
    #     stacks = inspect.stack()
    #     print("stack", len(stacks), *[f"{i}={s.function}" for i, s in enumerate(stacks)])

    #     return frame.f_locals

    def __getitem__(self, key):

        import inspect
        stacks = inspect.stack()
        print("get", len(stacks), *[f"{i}={s.function}" for i, s in enumerate(stacks)])

        from sys import _getframe
        frame = _getframe(self._stackidx)
        return frame.f_locals[key]

    def __setitem__(self, key, val):
        import inspect
        stacks = inspect.stack()
        print("set", len(stacks), *[f"{i}={s.function}" for i, s in enumerate(stacks)])

        from sys import _getframe
        frame = _getframe(self._stackidx)
        frame.f_locals[key] = val

    def __delitem__(self, key):
        from sys import _getframe
        frame = _getframe(self._stackidx)
        del frame.f_locals[key]

    def __contains__(self, key):
        from sys import _getframe
        frame = _getframe(self._stackidx)
        return key in frame.f_locals


# if eval("not not not 1"):  # False, only provided for Intellisense to work
#     ANY = anytype()
#     NEW = ctx(__remote_locals(3), _override=True, _pos=True)
#     NOT = ctx(__remote_locals(3), _override=False, _pos=False, _isroot=False)


def __init_module():
    import sys

    current_module = sys.modules[__name__]
    OldModuleClass = current_module.__class__

    class NewModuleClass(ctx, OldModuleClass):
        ...
    current_module.__class__ = NewModuleClass
    ctx.__init__(current_module, _data=__remote_locals(3), _override=False)


__init_module()
del __init_module
