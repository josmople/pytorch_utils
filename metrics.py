
def compute_ssim(img1, img2, window_size=11, size_average=True):
    from .lib import ssim as ssim_lib
    if img1.dim() == 3:
        img1 = img1.unsqueeze(0)
    if img2.dim() == 3:
        img2 = img2.unsqueeze(0)
    ssim = ssim_lib.ssim(img1, img2, window_size=window_size, size_average=size_average)
    return ssim


def compute_psnr(img1, img2, maxval=1.0):
    from torch.nn.functional import mse_loss
    from torch import log10
    if img1.dim() == 3:
        img1 = img1.unsqueeze(0)
    if img2.dim() == 3:
        img2 = img2.unsqueeze(0)
    mse = mse_loss(img1, img2)
    constant = 20 * log10(_torch.tensor(maxval))
    psnr = constant - 10 * log10(mse)
    return psnr
