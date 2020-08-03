
def gram(x):
    from torch import Tensor, bmm
    assert isinstance(x, Tensor)
    assert x.dim() == 4

    B, C, H, W = x.size()
    x = x.view(B, C, H * W)
    return bmm(x, x.permute(0, 2, 1)) / (H * W)


def covariance(x, eps=1e-8):
    from torch import Tensor, bmm
    assert isinstance(x, Tensor)
    assert x.dim() == 4

    B, C, H, W = x.size()
    x = x.view(B, C, H * W)
    x_mean = x.mean(dim=2, keepdim=True)
    x_std = x.std(dim=2, keepdim=True)
    x = (x - x_mean) / (x_std + eps)
    del x_mean, x_std
    return bmm(x, x.permute(0, 2, 1)) / (H * W)
