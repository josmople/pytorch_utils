import typing as _T

WILDCARD = ...

A = _T.TypeVar("A")
B = _T.TypeVar("B")
C = _T.TypeVar("C")
D = _T.TypeVar("D")


@_T.overload
def nple(n: _T.Literal[2], vals: _T.Tuple[A, B], clss: _T.Tuple[_T.Type[A], _T.Type[B]] = None) -> _T.Tuple[A, B]: ...
@_T.overload
def nple(n: _T.Literal[2], vals: _T.Tuple[A, A], clss: _T.Type[A] = None) -> _T.Tuple[A, A]: ...
@_T.overload
def nple(n: _T.Literal[2], vals: _T.Iterable[A], clss: _T.Type[A] = None) -> _T.Tuple[A, A]: ...
@_T.overload
def nple(n: _T.Literal[2], vals: A, clss: _T.Type[A] = None) -> _T.Tuple[A, A]: ...


@_T.overload
def nple(n: _T.Literal[3], vals: _T.Tuple[A, B, C], clss: _T.Tuple[_T.Type[A], _T.Type[B], _T.Type[C]] = None) -> _T.Tuple[A, B, C]: ...
@_T.overload
def nple(n: _T.Literal[3], vals: _T.Tuple[A, A, A], clss: _T.Type[A] = None) -> _T.Tuple[A, A, A]: ...
@_T.overload
def nple(n: _T.Literal[3], vals: _T.Iterable[A], clss: _T.Type[A] = None) -> _T.Tuple[A, A, A]: ...
@_T.overload
def nple(n: _T.Literal[3], vals: A, clss: _T.Type[A] = None) -> _T.Tuple[A, A, A]: ...


@_T.overload
def nple(n: _T.Literal[4], vals: _T.Tuple[A, B, C, D], clss: _T.Tuple[_T.Type[A], _T.Type[B], _T.Type[C], _T.Type[D]] = None) -> _T.Tuple[A, B, C, D]: ...
@_T.overload
def nple(n: _T.Literal[4], vals: _T.Tuple[A, A, A, A], clss: _T.Type[A] = None) -> _T.Tuple[A, A, A, A]: ...
@_T.overload
def nple(n: _T.Literal[4], vals: _T.Iterable[A], clss: _T.Type[A] = None) -> _T.Tuple[A, A, A, A]: ...
@_T.overload
def nple(n: _T.Literal[4], vals: A, clss: _T.Type[A] = None) -> _T.Tuple[A, A, A, A]: ...


@_T.overload
def nple(n: int, vals: _T.Iterable[A], clss: _T.Type[A] = None) -> _T.Tuple[A, ...]: ...
@_T.overload
def nple(n: int, vals: _T.Union[_T.Iterable, object], clss: _T.Union[type, _T.Iterable[type]] = None) -> tuple: ...


def nple(n: int, vals: object, clss: type = None) -> tuple:
    if isinstance(vals, _T.Iterable):
        vals = list(vals)
        assert len(vals) == n, f"Length of iterable must be {n} but got {len(vals)}"
    else:
        vals = [vals] * n

    if clss is None:
        clss = [WILDCARD] * n
    if isinstance(clss, type):
        clss = [clss] * n
    assert isinstance(clss, _T.Iterable), "Parameter clss must be a `type` or `Iterable[type]`"

    for i, (val, cls) in enumerate(zip(vals, clss)):
        if cls == WILDCARD:
            continue
        assert isinstance(val, cls), f"The {i}-th element must be of type {cls} but got {val.__class__} instead"

    return tuple(vals)
