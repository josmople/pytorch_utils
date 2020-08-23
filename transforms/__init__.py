from torchvision.transforms import *
del functional

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
            tensor (PyTorch Tensor): Tensor to set device.

        Returns:
            PyTorch Tensor: Changed device.
        """
        return functional.to_cuda(tensor, self.device)

    def __repr__(self):
        return self.__class__.__name__ + f'(device={self.device})'


class ReadImage(object):
    """Reads a path:str to PIL.Image.
    """

    def __init__(self):
        pass

    def __call__(self, path):
        """
        Args:
            path (str): File path of image.

        Returns:
            PIL Image: Image.
        """
        return functional.read_image(path)

    def __repr__(self):
        return self.__class__.__name__ + '()'


class ReadImageTensor(object):
    """Reads a path:str to PIL.Image to Pytorch Tensor.
    """

    def __init__(self):
        pass

    def __call__(self, path):
        """
        Args:
            path (str): File path of image.

        Returns:
            Pytorch Tensor: Tensor format of the image.
        """
        return functional.read_image_tensor(path)

    def __repr__(self):
        return self.__class__.__name__ + '()'


class Unsqueeze(object):
    """Performs unsqueeze operation to the tensor.
    If dim is an iterable, performs the unsqueeze operations sequentially.
    """

    def __init__(self, dim=0):
        self.dim = dim

    def __call__(self, tensor):
        """
        Args:
            tensor (torch.Tensor): Tensor to be unsqueezed

        Returns:
            Pytorch Tensor: Modified view of the tensor.
        """
        from torch import unsqueeze

        if isinstance(self.dim, int):
            return unsqueeze(tensor, self.dim)

        for dim in self.dim:
            tensor = unsqueeze(tensor, dim)
        return tensor

    def __repr__(self):
        return self.__class__.__name__ + f'(dim={self.dim})'


class Squeeze(object):
    """Performs squeeze operation to the tensor.
    If dim is an iterable, performs the squeeze operations sequentially.
    """

    def __init__(self, dim=None):
        self.dim = dim

    def __call__(self, tensor):
        """
        Args:
            tensor (torch.Tensor): Tensor to be unsqueezed

        Returns:
            Pytorch Tensor: Modified view of the tensor.
        """
        from torch import squeeze

        if self.dim is None:
            return squeeze(tensor)

        if isinstance(self.dim, int):
            return squeeze(tensor, self.dim)

        for dim in self.dim:
            tensor = squeeze(tensor, dim)
        return tensor

    def __repr__(self):
        return self.__class__.__name__ + f'(dim={self.dim})'


class DivisibleCrop(object):
    """Crops the image so that its length or width is divisible by the provided divisor.
    """

    def __init__(self, divisor):
        self.divisor = divisor

    def __call__(self, tensor):
        """
        Args:
            tensor (torch.Tensor): Image tensor to be cropped.

        Returns:
            Pytorch Tensor: Cropped tensor divisible by 'divisor'.
        """
        return functional.divisible_crop(tensor, self.divisor)

    def __repr__(self):
        return self.__class__.__name__ + f'(divisor={self.divisor})'


class Debug(object):

    def __init__(self, val_fn=lambda x: x, log_fn=print):
        self.val_fn = val_fn
        self.log_fn = log_fn

    def __call__(self, obj):
        if callable(self.val_fn) and callable(self.log_fn):
            self.log_fn(self.val_fn(obj))
        return obj
