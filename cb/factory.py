import typing as _T
from .nop import NOP

X = _T.TypeVar("X")


def from_list(*callbacks: _T.Union[_T.Callable, _T.Sequence[_T.Callable]], accumulator: _T.Callable[[_T.List[_T.Any]], _T.Any] = tuple) -> _T.Callable:
    assert callable(accumulator)

    saved_callbacks = []
    for callback in callbacks:
        if callable(callback):
            saved_callbacks.append(callback)
            continue

        for callback_sub in callback:
            assert callable(callback_sub)
            saved_callbacks.append(callback_sub)

    def generated_callback(*args, **kwds):
        outputs = []
        for cb in saved_callbacks:
            outputs.append(cb(*args, **kwds))
        return accumulator(outputs)

    return generated_callback


def from_dict(callbacks: _T.Dict[str, _T.Callable], default: _T.Union[_T.Callable, str] = "DEFAULT"):
    saved_callbacks = {}
    for name, callback in callbacks.items():
        if not callable(callback):  # If not callable assume an iterable
            callback = from_list(*callback)
        saved_callbacks[str(name)] = callback

    default_callback = None
    if isinstance(default, str):
        if default in callbacks:
            default_callback = callbacks[default]
    if callable(default):
        default_callback = default
    if not callable(default_callback):
        default_callback = lambda *args, **kwds: default

    def generated_callback(__event: str, *args, **kwds):
        __event = str(__event)
        if __event not in callbacks:
            return default_callback(*args, **kwds)
        return saved_callbacks[__event](*args, **kwds)

    return generated_callback


def from_object(obj, default="DEFAULT"):
    def generated_callback(__event: str, *args, **kwds):
        __event = str(__event)
        queried_callback = getattr(obj, __event, None)
        if not callable(queried_callback):
            queried_callback = getattr(obj, default, NOP)
        return queried_callback(*args, **kwds)

    return generated_callback
