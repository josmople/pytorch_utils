from torchvision.transforms import *
from . import functional


class ToCuda(object):
    """Sets the device of tensor to CUDA.

    Args:
        device (None or int): Desired output size of the crop. If size is an
            int instead of sequence like (h, w), a square crop (size, size) is
            made.
    """

    def __init__(self, device=None):
        self.device = device

    def __call__(self, tensor):
        """
        Args:
            tensor (PyTorch Tensor): Tensor to set device

        Returns:
            PyTorch Tensor: Changed device.
        """
        return functional.to_cuda(tensor, self.device)

    def __repr__(self):
        return self.__class__.__name__ + '(device={0})'.format(self.device)
