from __future__ import annotations
import typing as T


class iztype:  # Class flag
    def __eq__(self, other): raise NotImplementedError()


class operators:

    def __invert__(self) -> inverttype:
        return inverttype(self)

    def __and__(self, other) -> andtype:
        return andtype(self, other)

    def __rand__(self, other) -> andtype:
        return andtype(other, self)

    def __or__(self, other) -> ortype:
        return ortype(self, other)

    def __ror__(self, other) -> ortype:
        return ortype(other, self)

    def __add__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x + y, self, other)

    def __radd__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x + y, other, self)

    def __sub__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x - y, self, other)

    def __rsub__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x - y, other, self)

    def __mul__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x * y, self, other)

    def __rmul__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x * y, other, self)

    def __pow__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x ** y, self, other)

    def __rpow__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x ** y, other, self)

    def __mod__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x % y, self, other)

    def __rmod__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x % y, other, self)

    def __truediv__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x.__truediv__(y), self, other)

    def __rtruediv__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x.__truediv__(y), other, self)

    def __floordiv__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x // y, self, other)

    def __rfloordiv__(self, other) -> lambdatype:
        return lambdatype(lambda x, y: x // y, other, self)


class anytype(iztype, operators):
    INSTANCE: anytype
    def __new__(cls): return anytype.INSTANCE
    def __eq__(self, other): return True
    def __getattr__(self, key): return self
    def __str__(self): return "ANY"
    def __repr__(self): return "anytype.INSTANCE"


anytype.INSTANCE = object.__new__(anytype)


class valuetype(iztype, operators):
    init = False

    def __init__(self, value=None):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, valuetype):
            if (self.init, other.init) == (True, True):
                return self.value == other.value
            if (self.init, other.init) == (False, False):
                raise Exception(f"When computing equality between two {valuetype}, at least one should be initialized.")
            if (self.init, other.init) == (False, True):
                return self == other.value
            if (self.init, other.init) == (True, False):
                return other == self.value

        if self.init:
            return self.value == other

        self.value = other
        self.init = True
        return True

    def __str__(self): return repr(self.value)
    def __repr__(self): return f"valuetype(value={self.value!r}, init={self.init})"


class inverttype(iztype, operators):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value != other

    def __str__(self): return f"not {self.value!r}"
    def __repr__(self): return f"inverttype(value={self.value!r})"


class andtype(iztype, operators):
    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):  # Perform all __eq__ evaluations to init valuetypes
        return all(arg == other for arg in self.args)

    def __str__(self): return " & ".join(map(repr, self.args))
    def __repr__(self): return f"andtype({', '.join(map(repr, self.args))})"


class ortype(iztype, operators):

    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):  # Perform all __eq__ evaluations to init valuetypes
        return any(arg == other for arg in self.args)

    def __str__(self): return " | ".join(map(repr, self.args))
    def __repr__(self): return f"ortype({', '.join(map(repr, self.args))})"


class lambdatype(iztype, operators):

    def __init__(self, ops: T.Callable, *args):
        self.ops = ops
        self.args = args

    def extract_value(self, arg):
        if isinstance(arg, valuetype):
            if arg.init:
                return arg.value
            raise Exception(f"Cannot perform operations on uninitialized {valuetype}")
        return arg

    def __eq__(self, other):
        return self.ops(*map(self.extract_value, self.args)) == other

    def __str__(self): return f"{self.ops.__name__}({', '.join(map(repr, self.args))})"
    def __repr__(self): return f"lambdatype(ops={self.ops!r}, args={list(self.args)!r})"


class ctx:

    def __init__(self, data, default):
        assert callable(getattr(data, "__getitem__", None))
        assert callable(getattr(data, "__setitem__", None))
        assert callable(getattr(data, "__contains__", None))
        assert callable(default)
        self.φDATA = data
        self.φDEFAULT = default

    def __getattr__(self, key) -> valuetype:
        if key not in self.φDATA:
            self.φDATA[key] = self.φDEFAULT(key)
        return self.φDATA[key]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class root_ctx(ctx):

    def __init__(self, locals: T.Tuple[dict, int] = None):

        if locals is None:
            locals = 4

        if isinstance(locals, int):
            from sys import _getframe
            locals = _getframe(locals).f_locals

        def default_fn(name):
            return valuetype(...)

        super().__init__(locals, default_fn)

    @property
    def NEW(self):
        return new_ctx(self.φDATA)

    @property
    def NOT(self):
        return not_ctx(self.φDATA)


class not_ctx(ctx):

    def __init__(self, data):
        def default_fn(name):
            return valuetype(...)

        super().__init__(data, default_fn)

    def __getattr__(self, key) -> valuetype:
        if key not in self.φDATA:
            self.φDATA[key] = self.φDEFAULT(key)
        return ~self.φDATA[key]


class new_ctx(ctx):

    def __init__(self, data):
        def default_fn(name):
            return valuetype(...)

        super().__init__(data, default_fn)

    def __getattr__(self, key) -> valuetype:
        self.φDATA[key] = self.φDEFAULT(key)
        return self.φDATA[key]


class ctx:

    def __init__(self, _data: T.MutableMapping = None, _override: bool = False, _pos: bool = True, _isroot=True):
        self._data: T.MutableMapping = _data or {}
        self._override: bool = _override
        self._pos: bool = _pos
        self._isroot: bool = _isroot

    @property
    def ANY(self):
        return anytype.INSTANCE

    @property
    def NEW(self):
        assert self._isroot, "This functionality can only be access by root 'ctx'"
        return ctx(_data=self._data, _override=True, _pos=self._pos, _isroot=False)

    @property
    def NOT(self):
        return ctx(_data=self._data, _override=self._override, _pos=not self._pos, _isroot=False)

    def __getattr__(self, key) -> valuetype:
        if key not in self._data or self._override:
            self._data[key] = valuetype(value=None, empty=True, pos=True)
        output = self._data[key]
        if isinstance(output, invertabletype):
            return output if output.pos == self._pos else ~output
        return output

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class _remote_locals:

    def __init__(self, _stackidx):
        self._stackidx = _stackidx

    def __getitem__(self, key):
        from sys import _getframe
        frame = _getframe(self._stackidx)
        return frame.f_locals[key]

    def __setitem__(self, key, val):
        from sys import _getframe
        frame = _getframe(self._stackidx)
        frame.f_locals[key] = val

    def __contains__(self, key):
        from sys import _getframe
        frame = _getframe(self._stackidx)
        return key in frame.f_locals


# Make the 'module' emulate the 'ctx' class

ANY = anytype.INSTANCE
NEW = ctx(_remote_locals(2), _override=True, _pos=True, _isroot=False)
NOT = ctx(_remote_locals(2), _override=False, _pos=False, _isroot=False)


def __init_module():
    import sys

    current_module = sys.modules[__name__]
    OldModuleClass = current_module.__class__

    class NewModuleClass(OldModuleClass):
        def __getattr__(self, key) -> memtype:
            caller_locals = _remote_locals(3)
            if key not in caller_locals:
                caller_locals[key] = memtype(value=None, empty=True, pos=True)
            output = caller_locals[key]
            if isinstance(output, invertabletype):
                return output if output.pos else ~output
            return output
    current_module.__class__ = NewModuleClass


__init_module()
del __init_module
