
def compute_ssim(img1, img2, window_size=11, size_average=True):
    from .lib import ssim as ssim_lib
    if img1.dim() == 3:
        img1 = img1.unsqueeze(0)
    if img2.dim() == 3:
        img2 = img2.unsqueeze(0)
    ssim = ssim_lib.ssim(img1, img2, window_size=window_size, size_average=size_average)
    return ssim


def compute_psnr(img1, img2, maxval=1.0, minscore=1e-8):
    from torch.nn.functional import mse_loss
    from torch import zeros_like, log10, tensor
    if img1.dim() == 3:
        img1 = img1.unsqueeze(0)
    if img2.dim() == 3:
        img2 = img2.unsqueeze(0)
    mse = mse_loss(img1, img2)
    mse[mse == 0] = minscore
    constant = 20 * log10(tensor(maxval))
    psnr = constant - 10 * log10(mse)
    return psnr
