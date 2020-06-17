from .core import Logger


class PrintLogger(Logger):

    def __init__(self, config):
        self.config = config

        if not isinstance(getattr(config, "echo", None), bool):
            self.config.echo = True

        from string import Formatter
        if not isinstance(getattr(config, "formatter", None), Formatter):
            from .format import get_formatter
            setattr(self.config, "formatter", get_formatter())

    def __call__(self, text, output="in"):
        assert output in ["in", "out", "err"]

        if self.config.echo:
            from typing import TextIO
            if not isinstance(getattr(config, f"std{output}", None), TextIO):
                import sys
                setattr(self.config, f"std{output}", getattr(sys, f"std{output}"))

        if callable(getattr(self.config, "__getitem__", None)):
            out = self.formatter.vformat(text, self.config, self.config)
        else:
            out = self.formatter.vformat(text, [], self.config.__dict__)

        if self.config.echo:
            print(out, file=self.stdout)

        return out
