import typing as _T

Event = _T.TypeVar("Event")


class Callback(_T.Protocol[Event]):

    def __call__(self, _event: Event, *args, **kwds): ...


class SubscriptableCallback(Callback[Event]):

    def subscribe(self, _event: Event, _callback): ...
    def unsubscribe(self, _event: Event, _callback): ...
    def subscriptions(self) -> _T.List[_T.Tuple[Event, _T.Callable]]: ...


del _T, Event
