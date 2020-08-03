
def gram(x):
    from torch import Tensor, bmm
    assert isinstance(x, Tensor)
    assert x.dim() == 4

    N, C, H, W = x.size()
    x = x.view(N, C, H * W)
    return bmm(x, x.permute(0, 2, 1)) / (H * W)


def covariance(x, standardize=False, standardize_eps=1e-8):
    from torch import Tensor, bmm
    assert isinstance(x, Tensor)
    assert x.dim() == 4

    B, C, H, W = x.size()
    x = x.view(B, C, H * W)
    if standardize:
        x_mean = x.mean(dim=2, keepdim=True)
        x_std = x.std(dim=2, keepdim=True)
        x = (x - x_mean) / (x_std + standardize_eps)
        del x_mean, x_std
    return bmm(x, x.permute(0, 2, 1)) / (H * W)
