import typing as T

WILDCARD = ...


class size:

    def __init__(self, *sizes):
        self.sizes = sizes

    def __eq__(self, other):
        if len(self.sizes) != len(other):
            return False
        for a, b, in zip(self.sizes, other):
            if a == WILDCARD or b == WILDCARD:
                continue
            if a != b:
                return False
        return True


def __init_module():
    import sys
    current_module = sys.modules[__name__]

    OldModuleClass = current_module.__class__

    class NewModuleClass(OldModuleClass):
        def __getattr__(self, key):
            return self.WILDCARD

    current_module.__class__ = NewModuleClass

    del current_module.__init_module


__init_module()
