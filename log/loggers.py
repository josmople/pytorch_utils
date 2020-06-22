from .core import Logger as _Logger


class PrintLogger(Logger):

    def __init__(self, echo=True, stream=None):
        self.echo = echo

        from sys import stdout
        self.stream = stream or stdout

    def __call__(self, _shared, text, **kwds):
        try:
            vals = {k: getattr(_shared, k) for k in iter(_shared)}
        except:
            vals = {k: getattr(_shared, k) for k in dir(_shared)}
        vals.update(kwds)

        out = str(text).format(**vals)
        if self.echo:
            print(out, file=self.stream)
        return out


del _Logger
