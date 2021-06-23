from __future__ import annotations
import typing as _T

from .interface import Callback as _Callback, SubscriptableCallback as _SubscriptableCallback


class NopCallback(_Callback):
    instance: NopCallback = None

    def __call__(self, _event, *args, **kwds):
        return None


class NopSubscriptableCallback(_SubscriptableCallback):
    instance: NopSubscriptableCallback = None

    def __call__(self, _event, *args, **kwds):
        return None

    def subscribe(self, _event, _callback):
        return None

    def unsubscribe(self, _event, _callback):
        return None

    def subscriptions(self) -> _T.List[_T.Tuple[_T.Any, _T.Callable]]:
        return []


NopCallback.instance = NopCallback()
NopSubscriptableCallback.instance = NopSubscriptableCallback()

del _T, _Callback, _SubscriptableCallback
