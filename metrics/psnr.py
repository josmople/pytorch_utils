
def compute_psnr(a, b, maxval=1.0):
    from torch import Tensor
    assert isinstance(a, Tensor)
    assert isinstance(b, Tensor)
    mse = (a - b).pow(2).mean()
    if mse == 0:
        return 100
    constant = Tensor(maxval).to(device=a.get_device())
    return 20 * (constant / mse.sqrt()).log10()
