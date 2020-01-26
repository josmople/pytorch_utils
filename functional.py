import torch


def normalize(tensor, mean, std, inplace=False):
    if not inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    device = tensor.device

    mean = torch.as_tensor(mean, dtype=dtype, device=device)
    std = torch.as_tensor(std, dtype=dtype, device=device)

    if tensor.dim() == 3:
        tensor.sub_(mean[:, None, None]).div_(std[:, None, None])
    elif tensor.dim() == 4:
        tensor.sub_(mean[None, :, None, None]).div_(std[None, :, None, None])

    return tensor


def denormalize(tensor: torch.Tensor, mean, std, inplace=False):
    if not inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    device = tensor.device

    mean = torch.as_tensor(mean, dtype=dtype, device=device)
    std = torch.as_tensor(std, dtype=dtype, device=device)

    if tensor.dim() == 3:
        tensor.mul_(std[:, None, None]).add_(mean[:, None, None])
    elif tensor.dim() == 4:
        tensor.mul_(std[None, :, None, None]).add_(mean[None, :, None, None])

    return tensor
