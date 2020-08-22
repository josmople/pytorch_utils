
class ModuleRecordUtils:

    def __init__(self, label_attr="_rec_label", cache_attr="_rec_cache", class_attr="_rec_class", parent_attr="_rec_parent"):
        self.label_attr = label_attr
        self.cache_attr = cache_attr
        self.class_attr = class_attr
        self.parent_attr = parent_attr

    def record(self, module, label=None):
        from torch.nn import Module
        assert isinstance(module, Module)

        label_attr = self.label_attr
        cache_attr = self.cache_attr
        class_attr = self.class_attr
        parent_attr = self.parent_attr

        if label is None:
            label = f"{module.__class__.__name__}[id={id(module)}]"

        class RecordModule(module.__class__):
            def forward(self, *args, **kwds):
                out = super().forward(*args, **kwds)
                setattr(self, cache_attr, out)
                return out

        setattr(RecordModule, label_attr, label)
        setattr(RecordModule, cache_attr, None)
        setattr(RecordModule, class_attr, module.__class__)
        setattr(RecordModule, parent_attr, self)

        name = f"RecordModule[{module.__class__.__qualname__}]"
        RecordModule.__name__ = name
        RecordModule.__qualname__ = name

        module.__class__ = RecordModule
        return module

    def retrieve(self, modules, query=None):
        from collections import OrderedDict
        outputs = OrderedDict()

        label_attr, cache_attr = self.label_attr, self.cache_attr

        from torch.nn import Module
        for i, module in enumerate(modules):
            assert isinstance(module, Module), f"f{module} is not 'torch.nn.Module'"

            try:
                label = getattr(module, label_attr, i)
                if label in query:
                    cache = getattr(module, cache_attr)
                    outputs[label] = cache
            except AttributeError:
                pass

        return outputs

    def revert(self, modules):
        class_attr, parent_attr = self.class_attr, self.parent_attr

        from torch.nn import Module
        for module in modules:
            assert isinstance(module, Module), f"f{module} is not 'torch.nn.Module' but of type 'f{module.__class__.__name__}'"

            if getattr(module, parent_attr) is self:
                base_class = getattr(module, class_attr)
                assert issubclass(base_class, Module)
                module.__class__ = base_class

        return modules


_instance = ModuleRecordUtils()


def record(module, label=None):
    return _instance.record(module, label)


def retrieve(modules):
    return _instance.retrieve(modules)


def revert(modules):
    return _instance.revert(modules)
