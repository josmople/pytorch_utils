from __future__ import annotations


class NopCallback():
    INSTANCE: NopCallback

    def __new__(cls: type):
        return NopCallback.INSTANCE

    def __call__(self, *args, **kwds):
        return None


NOP = NopCallback.INSTANCE = object.__new__(NopCallback)
