import typing as _T
import torch as _th


class Resize:

    def __init__(self, mode="bilinear", size=None, scale=None, **kwds):
        self.mode: str = mode
        self.size: _T.Tuple[int, int] = size
        self.scale: _T.Tuple[int, int] = scale
        self.kwds = kwds

    def chw(self, tensor: _th.Tensor, *, mode=None, size=None, scale=None, **kwds) -> _th.Tensor:
        assert tensor.dim() == 3
        tensor = tensor.unsqueeze(0)
        tensor = self.bchw(tensor, mode=mode, size=size, scale=scale, **kwds)
        return tensor.squeeze(0)

    def bchw(self, tensor: _th.Tensor, *, mode=None, size=None, scale=None, **kwds) -> _th.Tensor:
        assert tensor.dim() == 4
        from torch.nn.functional import interpolate
        local_kwds = self.kwds.copy()
        local_kwds.update(kwds)
        return interpolate(tensor, size=(size or self.size), scale_factor=(scale or self.scale), mode=(mode or self.mode), **local_kwds)


bilinear = Resize("bilinear", align_corners=True)
bicubic = Resize("bicubic")
nearest = Resize("nearest")


def algo(mode: _T.Literal["bilinear", "bicubic", "nearest"] = "bilinear"):
    import sys
    return getattr(sys.modules[__name__], mode)
