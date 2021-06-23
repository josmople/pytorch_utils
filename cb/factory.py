import typing as _T

from .nop import NopCallback, NopSubscriptableCallback
from .simple import SimpleCallback


@_T.overload
def create(implementation="simple", subscriptable=True) -> SimpleCallback: ...
@_T.overload
def create(implementation="nop", subscriptable=True) -> NopSubscriptableCallback: ...
@_T.overload
def create(implementation="nop", subscriptable=False) -> NopCallback: ...


def create(implementation="simple", subscriptable=True):
    if implementation == "simple" and subscriptable:
        return SimpleCallback()

    if implementation == "nop":
        if subscriptable:
            return NopSubscriptableCallback.instance
        return NopCallback.instance

    raise NotImplementedError(f"No callback: implementation={implementation!r}, subscriptable={subscriptable}")
