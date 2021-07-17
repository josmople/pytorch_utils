from __future__ import annotations
import typing as _T

from .interface import SubscriptableCallback as _SubscriptableCallback


class CallableList(_T.List[_T.Callable]):

    def __call__(self, *args, **kwds):
        for callable in self:
            callable(*args, **kwds)


class EventAccessor:

    def __init__(self, address: _T.List[str], modifier: str):
        self.address = address
        self.modifier = modifier


class Node:

    class Context:

        def __init__(self, entry_fn, exit_fn, args, kwds):
            self.entry_fn = entry_fn
            self.exit_fn = exit_fn
            self.args = args
            self.kwds = kwds

        def __enter__(self):
            self.entry_fn(self.args, self.kwds)
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            try:
                exception = None if exc_type is None else (exc_value, exc_traceback)
                self.exit_fn(self.args, self.kwds, exception)
                return False
            except Exception as e:
                return True

    on_entry: CallableList
    on_exit: CallableList
    on_event: CallableList
    children: _T.Dict[str, Node]

    def __init__(self):
        self.on_entry = CallableList()
        self.on_exit = CallableList()
        self.on_event = CallableList()
        self.children = {}

    def __getitem__(self, idx):
        return self.children[idx]

    def __setitem__(self, idx, val):
        self.children[idx] = val

    def __delitem__(self, idx):
        del self.children[idx]

    def _context(self, args, kwds) -> Node.Context:
        return Node.Context(self.on_entry, self.on_exit, args, kwds)

    def add(self, _event: str):
        assert isinstance(_event, str)

        if _event not in self.children:
            self.children[_event] = Node()
        return self.children[_event]

    def find(self, _event: _T.Union[str, _T.List[str]]) -> _T.Generator[Node, None, None]:
        if _event == "*":
            for node in self.children.values():
                yield node
            return

        if isinstance(_event, (list, tuple)):
            for n in _event:
                if n in self.children:
                    yield self.children[n]
            return

        assert isinstance(_event, str)
        if _event in self.children:
            yield self.children[_event]

    def __call__(self, _event: _T.List[_T.Union[str, _T.List[str]]], *args, **kwds):

        with self._context():
            if len(_event) == 0:
                self.on_event(*args, **kwds)
                return

            event, *sub_events = _event
            for next in self.find(event):
                next(sub_events, *args, **kwds)


class ComplexCallback(_SubscriptableCallback[str]):

    def __init__(self) -> None:
        super().__init__()

    def subscribe(self, _event: str, _callback):
        return super().subscribe(_event, _callback)

    def unsubscribe(self, _event: str, _callback):
        return super().unsubscribe(_event, _callback)

    def subscriptions(self) -> _T.List[_T.Tuple[str, _T.Callable]]:
        return super().subscriptions()
