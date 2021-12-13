from __future__ import annotations
import typing as _T


class iztype:  # Class flag
    def __eq__(self, other): raise NotImplementedError()

    def __ne__(self, other):
        return not self.__eq__(other)


_O = _T.TypeVar("_O")


class operators:

    # Delayed Initialization
    def __call__(self: _O, *args, **kwds) -> _O:
        self.__init__(*args, **kwds)
        return self

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

    def __lt__(self, other) -> bool:
        return lambdatype(lambda x, y: x < y, self, other) == True

    def __le__(self, other) -> bool:
        return lambdatype(lambda x, y: x <= y, self, other) == True

    def __gt__(self, other) -> bool:
        return lambdatype(lambda x, y: x > y, self, other) == True

    def __ge__(self, other) -> bool:
        return lambdatype(lambda x, y: x >= y, self, other) == True


class anytype(iztype, operators):
    INSTANCE: anytype
    def __new__(cls): return anytype.INSTANCE
    def __eq__(self, other): return True
    def __call__(self): return self
    def __getattr__(self, key): return self
    def __str__(self): return "ANY"
    def __repr__(self): return "anytype.INSTANCE"


anytype.INSTANCE = object.__new__(anytype)


class valuetype(iztype, operators):
    UNINITIALIZED = object()  # Unique

    init = False
    value = UNINITIALIZED

    def __init__(self, value=UNINITIALIZED):
        if value != valuetype.UNINITIALIZED:
            self.value = value
            self.init = True

    def __eq__(self, other):
        if isinstance(other, valuetype):
            if self.init == True and other.init == True:
                return self.value == other.value
            if self.init == False and other.init == False:
                raise Exception(f"When computing equality '=' between two {valuetype}, at least one should be initialized.")
            if self.init == False and other.init == True:
                return self == other.value
            if self.init == True and other.init == False:
                return other == self.value

        if self.init:
            return self.value == other

        self.__init__(other)
        return True

    def __ne__(self, other):
        if self.init:
            return not self.__eq__(other)
        raise Exception(f"When computing inequality '!=', {valuetype} must be initialized.")

    def __str__(self): return f"{self.value!r}"
    def __repr__(self): return f"valuetype(value={self.value!r}, init={self.init})"


class inverttype(iztype, operators):
    UNINITIALIZED = object()  # Unique

    init = False
    value = UNINITIALIZED

    def __init__(self, value=UNINITIALIZED):
        if value != valuetype.UNINITIALIZED:
            self.value = value
            self.init = True

    def __eq__(self, other):
        if self.init:
            return self.value != other
        raise Exception(f"This {inverttype} is not initialized")

    def __str__(self): return f"not {self.value!r}"
    def __repr__(self): return f"valuetype(value={self.value!r}, init={self.init})"


class andtype(iztype, operators):
    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):
        vals = list(arg == other for arg in self.args)  # Perform all __eq__ evaluations to init valuetypes
        return all(vals)

    def __str__(self): return " & ".join(map(repr, self.args))
    def __repr__(self): return f"andtype({', '.join(map(repr, self.args))})"


class ortype(iztype, operators):

    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):
        vals = list(arg == other for arg in self.args)  # Perform all __eq__ evaluations to init valuetypes
        return any(vals)

    def __str__(self): return " | ".join(map(repr, self.args))
    def __repr__(self): return f"ortype({', '.join(map(repr, self.args))})"


class lambdatype(iztype, operators):

    def __init__(self, ops, *args):
        if not callable(ops):
            raise ValueError("Parameter 'ops' must be callable")
        self.ops = ops
        self.args = args

    def extract_value(self, arg):
        if isinstance(arg, valuetype):
            if arg.init:
                return arg.value
            raise valuetype(f"Cannot perform operation {self.ops} on uninitialized {valuetype}")
        return arg

    def __eq__(self, other):
        return self.ops(*map(self.extract_value, self.args)) == other

    def __str__(self): return f"{self.ops.__name__}({', '.join(map(repr, self.args))})"
    def __repr__(self): return f"lambdatype(ops={self.ops!r}, args={list(self.args)!r})"
