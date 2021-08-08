from . import classes, context


ANY = classes.anytype.INSTANCE

NOT: context.not_ctx
NEW: context.new_ctx


def __init_module():
    import sys

    current_module = sys.modules[__name__]
    OldModuleClass = current_module.__class__

    from sys import _getframe

    class NewModuleClass(OldModuleClass):
        def __call__(self):
            return context.root_ctx({})

        @property
        def NOT(self):
            locals_dict = _getframe(2).f_locals
            return context.not_ctx(locals_dict)

        @property
        def NEW(self):
            locals_dict = _getframe(2).f_locals
            return context.new_ctx(locals_dict)

        def __getattr__(self, key):
            locals_dict = _getframe(2).f_locals
            if key not in locals_dict:
                locals_dict[key] = classes.valuetype()
            return locals_dict[key]

    current_module.__class__ = NewModuleClass


__init_module()
del __init_module
