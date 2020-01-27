from .img import pil_loader as _default_image_loader


class PathToImage:

    def __init__(self, loader=_default_image_loader):
        self.loader = loader

    def __call__(self, path):
        return self.loader(path)


def normalize(tensor, mean, std, inplace=False):
    from torch import as_tensor

    if not inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    device = tensor.device

    mean = as_tensor(mean, dtype=dtype, device=device)
    std = as_tensor(std, dtype=dtype, device=device)

    if tensor.dim() == 3:
        tensor.sub_(mean[:, None, None]).div_(std[:, None, None])
    elif tensor.dim() == 4:
        tensor.sub_(mean[None, :, None, None]).div_(std[None, :, None, None])

    return tensor


def denormalize(tensor, mean, std, inplace=False):
    from torch import as_tensor

    if not inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    device = tensor.device

    mean = as_tensor(mean, dtype=dtype, device=device)
    std = as_tensor(std, dtype=dtype, device=device)

    if tensor.dim() == 3:
        tensor.mul_(std[:, None, None]).add_(mean[:, None, None])
    elif tensor.dim() == 4:
        tensor.mul_(std[None, :, None, None]).add_(mean[None, :, None, None])

    return tensor
