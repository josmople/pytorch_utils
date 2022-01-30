import typing as _T
import rx
import rx.subject
import rx.operators

_FN = _T.TypeVar("_FN", _T.Callable)


class Subscription:

    def __str__(self):
        raise NotImplementedError()

    def __subscribe__(self, subscriptable, callback):
        raise NotImplementedError()


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
    def subscribe(self, __event: Subscription) -> _T.Callable[[_FN], _FN]: ...
    @_T.overload
    def subscribe(self, __event: Subscription, __callback: _T.Callable) -> _T.Callable[[], None]: ...

    def subscribe(self, __event: Subscription, __callback: _T.Callable = None):
        __event = str(__event)

        if __callback is None:
            def decorator(callback):
                self.subscribe(__event, callback)
                return callback
            return decorator

        self.callbacks[__event].append(__callback)

        return self
