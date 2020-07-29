
def gram(x):
    from torch import Tensor, bmm
    assert isinstance(x, Tensor)
    assert x.dim() == 4

    N, C, H, W = x.size()
    x = x.view(N, C, H * W)
    return bmm(x, x.permute(0, 2, 1)) / (C * H * W)


def covariance(x, eps=1e-8):
    from torch import Tensor, bmm
    assert isinstance(x, Tensor)
    assert x.dim() == 4

    B, C, H, W = x.size()
    x_hat = x.view(B, C, H * W)
    x_mean = x_hat.mean(dim=2, keepdim=True)
    x_std = x_hat.std(dim=2, keepdim=True)
    x_norm = (x_hat - x_mean) / (x_std + eps)
    del x_hat, x_mean, x_std
    return bmm(x_norm, x_norm.permute(0, 2, 1)) / (H * W)
