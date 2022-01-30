from __future__ import annotations
import typing as _T

_FN = _T.TypeVar("_FN", _T.Callable)


class SubscriptableCallback:

    def __init__(self):
        self.callbacks: _T.Dict[str, _T.List[_T.Callable]] = {}

    def __call__(self, __event, *args, **kwds):
        self.invoke(__event, *args, **kwds)

    def invoke(self, __event, *args, **kwds):
        __event = str(__event)

        if __event in self.callbacks:
            callbacks = self.callbacks[__event]
            for callback in callbacks:
                callback(*args, **kwds)

    @_T.overload
    def subscribe(self, __event: str) -> _T.Callable[[_FN], _FN]: ...
    @_T.overload
    def subscribe(self, __event: str, *__callbacks: _T.Callable) -> SubscriptableCallback: ...

    def subscribe(self, __event: str, *__callbacks: _T.Callable):
        __event = str(__event)

        if len(__callbacks) == 0:
            def decorator(callback):
                self.subscribe(__event, callback)
                return callback
            return decorator

        if __event not in self.callbacks:
            self.callbacks[__event] = []
        for callback in __callbacks:
            self.callbacks[__event].append(callback)

        return self

    def unsubscribe(self, __event: str, *__callbacks: _T.Callable) -> _T.List[_T.Callable]:
        __event = str(__event)

        if __event not in self.callbacks:
            return None

        removed__callbacks = []

        event__callbacks = self.callbacks[__event]
        for callback in __callbacks:
            try:
                event__callbacks.remove(callback)
                removed__callbacks.append(callback)
            except ValueError:
                pass

        return removed__callbacks

    def subscriptions(self) -> _T.List[_T.Tuple[str, _T.Callable]]:
        def generator():
            for event, callbacks in self.callbacks.items():
                for callback in callbacks:
                    yield event, callback
        return list(generator())
