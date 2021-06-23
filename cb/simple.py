from __future__ import annotations
import typing as _T

from .interface import SubscriptableCallback as _SubscriptableCallback


class SimpleCallback(_SubscriptableCallback[str]):

    def __init__(self):
        self.callbacks: _T.Dict[str, _T.List[_T.Callable]] = {}

    def __call__(self, _event, *args, **kwds):
        self.invoke(_event, *args, **kwds)

    def invoke(self, _event, *args, **kwds):
        if _event in self.callbacks:
            callbacks = self.callbacks[_event]
            for callback in callbacks:
                callback(*args, **kwds)

    @_T.overload
    def subscribe(self, _event: str) -> _T.Callable: ...
    @_T.overload
    def subscribe(self, _event: str, *_callbacks: _T.Callable) -> SimpleCallback: ...

    def subscribe(self, _event: str, *_callbacks: _T.Callable):
        if len(_callbacks) == 0:
            from functools import partial
            return partial(self.subscribe, _event)

        if _event not in self.callbacks:
            self.callbacks[_event] = []
        for callback in _callbacks:
            self.callbacks[_event].append(callback)

        return self

    def unsubscribe(self, _event: str, *_callbacks: _T.Callable) -> _T.List[_T.Callable]:
        if _event not in self.callbacks:
            return None

        removed_callbacks = []

        event_callbacks = self.callbacks[_event]
        for callback in _callbacks:
            try:
                event_callbacks.remove(callback)
                removed_callbacks.append(callback)
            except ValueError:
                pass

        return removed_callbacks

    def subscriptions(self) -> _T.List[_T.Tuple[str, _T.Callable]]:
        def generator():
            for event in self.callbacks:
                for callback in self.callbacks[event]:
                    yield event, callback
        return list(generator())


del _T, _SubscriptableCallback
