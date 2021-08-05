from __future__ import annotations
import typing as T


class any_type:
    def __getattr__(self, key):
        return self

    def __eq__(self, other):
        return True

    def __str__(self):
        return "ANY"

    def __repr__(self):
        return "ANY"


class mem(dict):

    ANY: any_type

    class unit:
        __slots__ = "val", "empty"

        def __init__(self, val=None, empty=True):
            self.val = val
            self.empty = empty

        def __str__(self):
            return str(self.val)

        def __repr__(self):
            return f"mem.unit(val={self.val!r}, empty={self.empty})"

    def __getattr__(self, key) -> mem.unit:
        if key not in self:
            self[key] = mem.unit(val=None, empty=True)
        return self[key]


ANY = mem.ANY = any_type()


class size:

    def __init__(self, *sizes):
        self.sizes = sizes

    def __eq__(self, other):
        if len(self.sizes) != len(other):
            return False
        for a, b, in zip(self.sizes, other):
            if isinstance(a, mem.unit) and isinstance(b, mem.unit):
                raise Exception(f"Left ({a}) and right ({b}) operand must not be both `mem.unit`")

            if isinstance(a, mem.unit):
                b_val = b.val if isinstance(b, mem.unit) else b
                if a.empty:
                    a.val = b_val
                    a.empty = False
                if a.val != b_val:
                    return False
                continue

            if isinstance(b, mem.unit):
                a_val = a.val if isinstance(a, mem.unit) else a
                if b.empty:
                    b.val = a_val
                    b.empty = False
                if b.val != a_val:
                    return False
                continue

            if a != b:
                return False

        return True


# def __init_module():
#     import sys
#     current_module = sys.modules[__name__]

#     OldModuleClass = current_module.__class__

#     class NewModuleClass(OldModuleClass):
#         def __getattr__(self, key):
#             return self.WILDCARD

#     current_module.__class__ = NewModuleClass

#     del current_module.__init_module


# __init_module()
