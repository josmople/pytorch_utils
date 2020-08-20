
def compute_psnr(a, b, maxval=1.0):
    from torch import Tensor, tensor
    assert isinstance(a, Tensor)
    assert isinstance(b, Tensor)
    mse = (a - b).pow(2).mean()
    if mse == 0:
        return 100
    device = a.get_device()
    constant = tensor(maxval)
    constant = constant.cpu() if device < 0 else constant.to(device=device)
    return 20 * (constant / mse.sqrt()).log10()
