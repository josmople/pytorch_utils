import typing as _T


class Resize:

    def __init__(self, mode="bilinear", size=None):
        self.mode: str = mode
        self.size: _T.Tuple[int, int] = size

    def chw(self, tensor, size=None, mode=None):
        from torchvision.transforms.functional import resize, InterpolationMode
        return resize(tensor, size=size or self.size, interpolation=getattr(InterpolationMode, (mode or self.mode).upper()))

    def bchw(self, tensor, size=None, mode=None):
        from torch.nn.functional import interpolate
        return interpolate(tensor, size=size or self.size, mode=(mode or self.mode))


bilinear = Resize("bilinear")
bicubic = Resize("bicubic")
nearest = Resize("nearest")
