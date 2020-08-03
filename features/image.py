
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
    x.sub_(x.mean(dim=2, keepdim=True))
    x.div_(x.std(dim=2, keepdim=True) + eps)
    return bmm(x, x.permute(0, 2, 1)) / (H * W)
