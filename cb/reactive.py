from __future__ import annotations
import typing as _T

import rx
import rx.disposable
import rx.subject
import rx.operators

X = _T.TypeVar("X")


class ReactiveParameters(_T.NamedTuple):
    event: object
    args: list
    kwds: dict


class ReactiveSubscription(_T.Protocol[X]):

    def __call__(self, stream: rx.Observable[X], callback: _T.Callable) -> rx.disposable.Disposable:
        raise NotImplementedError()


def from_subscriptions(
    subscriptions: _T.List[_T.Tuple[ReactiveSubscription, _T.Callable]],
    subject_builder: _T.Callable[[], rx.subject.Subject] = rx.subject.Subject,
    parameter_builder: _T.Callable[[object, list, dict], _T.Any] = ReactiveParameters
):
    stream = subject_builder()
    for subscription, callback in subscriptions:
        subscription(stream, callback)

    def generated_callback(__event, *args, **kwds):
        try:
            return stream.on_next(parameter_builder(__event, args, kwds))
        except e:
            return stream.on_error(e)

    return generated_callback


class ReactiveCallback:

    def __init__(self) -> None:
        self.stream: rx.subject.Subject = None
        self.subscriptions: _T.List[_T.Tuple[ReactiveSubscription, _T.Callable]] = []

    def parameters(self, event, args, kwds):
        return ReactiveParameters(str(event), args, kwds)

    def __call__(self, __event, *args, **kwds):
        if self.stream is None:
            self.build()

        try:
            self.stream.on_next(self.parameters(__event, args, kwds))
        except Exception as error:
            self.stream.on_error(error)

    def build(self):
        self.close()

        self.stream = rx.subject.Subject()
        for subscription, callback in self.subscriptions:
            subscription.__subscribe__(self.stream, callback)

        return self.stream

    def close(self):
        if self.stream is not None:
            self.stream.on_completed()
        self.stream = None


class Events(_T.NamedTuple):

    def __init__(
        self,
        streams: _T.List[rx.Observable] = [],
        events: _T.List[str] = [],
        intervals: _T.List[int] = [],
        predicates: _T.List[_T.Callable[...], bool] = [],
        is_once: bool = False,
        has_event: bool = False,
    ):
        self.streams = list(streams)
        self.events = list(events)
        self.intervals = list(intervals)
        self.predicates = list(predicates)
        self.is_once = is_once
        self.has_event = has_event

    def update(
        self: Events,
        cls: _T.Type[Events],
        streams: _T.List[rx.Observable] = [],
        events: _T.List[str] = [],
        intervals: _T.List[int] = [],
        predicates: _T.List[_T.Callable[...], bool] = [],
        is_once: bool = None,
        has_event: bool = None,
    ):
        if self is None:
            self = cls()

        new_streams = [*self.streams, *streams]
        new_events = list(map(str, [*self.events, *events]))
        new_predicates = [*self.predicates, *predicates]
        new_intervals = list(map(int, [*self.intervals, *intervals]))
        new_is_once = self.is_once if is_once is None else bool(is_once)
        new_has_event = self.has_event if has_event is None else bool(has_event)

        assert all([isinstance(s, rx.Observable) for s in new_streams])
        assert all([callable(p) for p in new_predicates])

        return Events(
            streams=new_streams,
            events=new_events,
            predicates=new_predicates,
            intervals=new_intervals,
            is_once=new_is_once,
            has_event=new_has_event,
        )

    def on(self, cls, *events: str):
        if self is None:
            self = cls()
        return self.update(events=events)

    def when(self, cls, *predicates: _T.Callable):
        if self is None:
            self = cls()
        return self.update(predicates=predicates)

    def every(self, cls, *intervals: int):
        if self is None:
            self = cls()
        return self.update(intervals=intervals)

    def once(self, cls):
        if self is None:
            self = cls()
        return self.update(is_once=True)

    def event_param(self, cls):
        if self is None:
            self = cls()
        return self.update(has_event=True)

    def listen(self, *stream: rx.Observable):
        return Events(streams=stream, event=self.events, predicate=self.predicates, interval=self.intervals, is_once=self.is_once, has_event=self.has_event)

    def __call__(self, handler: _T.Callable):
        disposables = []
        for stream in self.streams:
            events = self.events
            stream = rx.operators.filter(lambda data: data[0] in events)(stream)

            for predicate in self.predicates:
                assert callable(predicate)
                stream = rx.operators.filter(predicate)(stream)

            for interval in self.intervals:
                interval = int(interval)
                stream = rx.operators.filter_indexed(lambda data, index: index % interval == 0)(stream)

            if self.is_once:
                stream = rx.operators.first()(stream)

            if self.has_event:
                disposable = stream.subscribe(lambda inputs: handler(inputs[0], *inputs[1], **inputs[2]))
            else:
                disposable = stream.subscribe(lambda inputs: handler(*inputs[1], **inputs[2]))

            disposables.append(disposable)
        return rx.disposable.CompositeDisposable(disposables)

    def __str__(self):
        return str(self.events)


e = Events()
e.every()


class On:

    def __init__(self, event: str):
        self.event = str(event)

    def __call__(self, fn: _T.Callable):

        return fn
