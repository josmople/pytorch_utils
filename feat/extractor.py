import typing as _T
from torch import Tensor as _Tensor
from torch.nn import Module as _Module


class FeatureExtractor(_Module):

    class EarlyExit(Exception):
        pass

    def __init__(self, model: _Module, targets: _T.List[str], early_exit=True):
        super().__init__()

        self.model: _Module = model
        self.targets: _T.List[str] = targets
        self.outputs: _T.Dict[str, _Tensor] = {}
        self.early_exit = early_exit

        from torch.utils.hooks import RemovableHandle
        self._handles: _T.List[RemovableHandle] = None

        self.hook_model()

    def hook_model(self):
        assert self._handles is None, f"The model ({self.model.__class__.__name__}) is already hooked"

        self._handles = []
        for name, submodule in self.model.named_modules():
            if name in self.targets:
                hook = self.generate_hook(name)
                handle = submodule.register_forward_hook(hook)
                self._handles.append(handle)

    def unhook_model(self):
        assert self._handles is not None, f"The model ({self.model.__class__.__name__}) is not hooked yet"

        for handle in self._handles:
            handle.remove()
        self._handles = None

    def generate_hook(self, name):
        def hook(module, input, output):
            self.outputs[name] = output
            # Exit immediately if all target outputs are accounted for
            if self.early_exit and all([layer in self.outputs for layer in self.targets]):
                raise FeatureExtractor.EarlyExit()
        return hook

    def forward(self, *args, **kwds):
        assert self._handles is not None, f"The model ({self.model.__class__.__name__}) is not hooked yet"

        try:
            self.outputs = {}
            self.model(*args, **kwds)
        except FeatureExtractor.EarlyExit:
            pass

        outputs = self.outputs
        outputs = [outputs[name] for name in self.targets]

        self.outputs = {}
        return outputs


del _T, _Module, _Tensor
