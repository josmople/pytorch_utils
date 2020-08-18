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
            tensor (PyTorch Tensor): Tensor to set device

        Returns:
            PyTorch Tensor: Changed device.
        """
        return functional.to_cuda(tensor, self.device)

    def __repr__(self):
        return self.__class__.__name__ + '(device={0})'.format(self.device)


class ReadImage(object):
    """Reads a path:str to PIL.Image
    """

    def __init__(self):
        pass

    def __call__(self, path):
        """
        Args:
            path (str): File path of image

        Returns:
            PIL Image: Image.
        """
        return functional.read_image(path)

    def __repr__(self):
        return self.__class__.__name__ + '()'


class ReadImageTensor(object):
    """Reads a path:str to PIL.Image to Pytorch Tensor
    """

    def __init__(self):
        pass

    def __call__(self, path):
        """
        Args:
            path (str): File path of image

        Returns:
            Pytorch Tensor: Tensor format of the image.
        """
        return functional.read_image_tensor(path)

    def __repr__(self):
        return self.__class__.__name__ + '()'
