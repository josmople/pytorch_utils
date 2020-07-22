
def compute_psnr(a, b, maxval=1.0, minscore=1e-8):
    from torch.nn.functional import mse_loss
    from torch import zeros_like, log10, tensor
    if a.dim() == 3:
        a = a.unsqueeze(0)
    if b.dim() == 3:
        b = b.unsqueeze(0)
    mse = mse_loss(a, b)
    mse[mse == 0] = minscore
    constant = 20 * log10(tensor(maxval))
    psnr = constant - 10 * log10(mse)
    return psnr
