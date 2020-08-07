from torchvision.transforms.functional import *


def to_cuda(tensor, device=None):
    if device is None:
        return tensor.cuda()
    else:
        return tensor.to(device=device)
