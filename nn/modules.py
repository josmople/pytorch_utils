from torch.nn import Module as _Module


class Lambda(_Module):

    def __init__(self, fn):
        super().__init__()
        assert callable(fn)
        self.fn = fn

    def forward(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


del _Module
