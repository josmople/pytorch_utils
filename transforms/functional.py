from torchvision.transforms.functional import *


def to_cuda(tensor, device=None):
    if device is None:
        return tensor.cuda()
    if int(device) < 0:
        return tensor.cpu()
    return tensor.to(device=device)


def read_image(path):
    from PIL import Image
    return Image.open(path)


def read_image_tensor(path):
    return to_tensor(read_image(path))


def divisible_crop(tensor, divisor):
    if isinstance(divisor, int):
        divh = divisor
        divw = divisor
    else:
        divh = divisor[0]
        divw = divisor[1]

    _, h, w = tensor.size()
    xtra_h, xtra_w = h % divh, w % divw
    new_h, new_w = h - xtra_h, w - xtra_w
    return tensor[:, :new_h, :new_w]
