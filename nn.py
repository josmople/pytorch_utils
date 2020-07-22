from torch.nn import Module as _Module


def pad(padtype, padding, dim=2):
    import torch.nn.modules.padding as pads

    if padtype is None or padtype == "zero":
        if dim == 2:
            return pads.ZeroPad2d(padding)

    if padtype == "reflect":
        if dim == 1:
            return pads.ReflectionPad1d(padding)
        if dim == 2:
            return pads.ReflectionPad2d(padding)

    if padtype == "replicate":
        if dim == 1:
            return pads.ReplicationPad1d(padding)
        if dim == 2:
            return pads.ReplicationPad2d(padding)
        if dim == 3:
            return pads.ReplicationPad3d(padding)

    if isinstance(padtype, (int, float, tuple)):
        if isinstance(padtype, tuple):
            assert all([isinstance(n, (int, float)) for n in padtype])

        if dim == 1:
            return pads.ConstantPad1d(padding, padtype)
        if dim == 2:
            return pads.ConstantPad2d(padding, padtype)
        if dim == 3:
            return pads.ConstantPad3d(padding, padtype)

    raise NotImplementedError(f"No such padding type: {padtype}-{dim}d")


def act(acttype, **kwargs):
    from torch.nn import Module
    import torch.nn.modules.activation as acts
    import inspect

    for n in dir(acts):
        obj = getattr(acts, n)
        if inspect.isclass(obj) and issubclass(obj, Module):
            if acttype.lower() == n.lower():
                return obj(**kwargs)

    raise NotImplementedError(f"No such activation type: {acttype}")


class Lambda(_Module):

    def __init__(self, fn):
        super().__init__()
        assert callable(fn)
        self.fn = fn

    def forward(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
