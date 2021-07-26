import typing as _T
from torch import Tensor as _Tensor
from torch.nn import Module as _Module


class hook_output(_T.NamedTuple):
    forward: _T.Callable[[_T.Any], _T.List[_Tensor]]
    unhook: _T.Callable[[], None]
    cache: _T.Callable[[], _T.Dict[str, _Tensor]]


def hook(model: _Module, targets: _T.List[_T.Union[str, _Module]], early_exit=True) -> hook_output:
    from torch.utils.hooks import RemovableHandle

    class EarlyExit(Exception):
        pass

    targets: _T.List[str, _Module] = list(targets)
    outputs: _T.Dict[str, _Tensor] = {}
    handles: _T.List[RemovableHandle] = []
    state: _T.Dict[str, _Tensor] = {"in-context": False}

    for name, submodule in model.named_modules():
        if (name in targets) or (submodule in targets):

            if early_exit:
                def hook(module, input, output):
                    if state["in-context"]:
                        outputs[name] = output
                        if all([layer in outputs for layer in targets]):  # If all target outputs are accounted
                            raise EarlyExit()  # Exit immediately
            else:
                def hook(module, input, output):
                    if state["in-context"]:
                        outputs[name] = output

            handle = submodule.register_forward_hook(hook)
            handles.append(handle)

    def forward(*args, **kwds) -> _T.List[_Tensor]:
        try:
            state["in-context"] = True
            outputs.clear()
            model(*args, **kwds)
        except EarlyExit:
            pass
        finally:
            state["in-context"] = False

        results = [outputs[name] for name in targets]
        return results

    def unhook():
        for handle in handles:
            handle.remove()

    def cache() -> _T.Dict[str, _Tensor]:
        return dict(outputs)

    return hook_output(forward, unhook, cache)


class FeatureExtractor(_Module):

    def __init__(self, model: _Module, targets: _T.List[str], early_exit=True):
        super().__init__()

        self._model: _Module = None
        self.hook_model(model=model, targets=targets, early_exit=early_exit)

    def hook_model(self, model: _Module, targets: _T.List[str], early_exit=True):
        assert self._model is None, f"The model ({self.model.__class__.__name__}) is already hooked"

        invoke, unhook, cache = hook(model, targets=targets, early_exit=early_exit)

        self._model = model
        self._invoke = invoke
        self._unhook = unhook
        self._cache = cache

    def unhook_model(self):
        assert self._model is not None, f"The model ({self.model.__class__.__name__}) is not hooked yet"

        self._unhook()

        self._model = None
        self._invoke = None
        self._unhook = None
        self._cache = None

    def rehook_model(self, model: _Module, targets: _T.List[str], early_exit=True):
        if self._model is not None:
            self.unhook_model()
        self.hook_model(model=model, targets=targets, early_exit=early_exit)

    def forward(self, *args, **kwds):
        assert self._model is not None, f"The model ({self.model.__class__.__name__}) is not hooked yet"
        return self._invoke(*args, **kwds)


del _T, _Module, _Tensor
