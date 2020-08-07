from torchvision.transforms.functional import *


def to_cuda(tensor, device=None):
    if device is None:
        return tensor.cuda()
    else:
        return tensor.to(device=device)


def read_image(path):
    from PIL import Image
    return Image.open(path)


def read_image_tensor(path):
    return to_tensor(read_image(path))
