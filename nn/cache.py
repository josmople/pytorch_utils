
class ModuleRecordUtils:

    def __init__(self, label_attr="_rec_label", cache_attr="_rec_cache"):
        self.label_attr = label_attr
        self.cache_attr = cache_attr

    def record(self, module, label=None):
        from torch.nn import Module
        assert isinstance(module, Module)

        label_attr, cache_attr = self.label_attr, self.cache_attr

        if label is None:
            label = f"{module.__class__.__name__}[id={id(module)}]"

        class RecordModule(module.__class__):
            def forward(self, *args, **kwds):
                out = super().forward(*args, **kwds)
                setattr(self, cache_attr, out)
                return out

        setattr(module, label_attr, label)
        setattr(module, cache_attr, None)

        module.__class__ = RecordModule
        return module

    def retrieve(self, modules, label_attr="_rec_label", cache_attr="_rec_cache"):
        from collections import OrderedDict
        outputs = OrderedDict()
        marker = {}

        label_attr, cache_attr = self.label_attr, self.cache_attr

        from torch.nn import Module
        for i, module in enumerate(modules):
            assert isinstance(module, Module), f"f{module} is not 'torch.nn.Module' but of type 'f{module.__class__.__name__}'"

            cache = getattr(module, cache_attr, marker)
            if cache is not marker:
                label = getattr(module, label_attr, i)
                outputs[label] = cache

        return outputs

    def restore(self, modules):
        label_attr, cache_attr = self.label_attr, self.cache_attr

        from torch.nn import Module
        for module in modules:
            assert isinstance(module, Module), f"f{module} is not 'torch.nn.Module' but of type 'f{module.__class__.__name__}'"

            delattr(module, label_attr)
            delattr(module, cache_attr)

            orig_module = module.__class__.__bases[0]
            assert issubclass(orig_module, Module)

            module.__class__ = orig_module

        return modules


_instance = ModuleRecordUtils()

record = _instance.record
retrieve = _instance.retrieve
restore = _instance.restore
