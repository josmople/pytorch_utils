import typing as _T
import torch.nn as _nn
from .extractor import FeatureExtractor as _FeatureExtractor

import torchvision.models.vgg as base

NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]

NORMALIZE_MEAN_255 = [v * 255 for v in NORMALIZE_MEAN]
NORMALIZE_STD_255 = [v * 255 for v in NORMALIZE_STD]


def normalize(tensor, mean=NORMALIZE_MEAN, std=NORMALIZE_STD, inplace=False):
    """
    Normalizes image tensor using VGG mean and std.
    Assumes image has [0,1] values.
    Accepts CxHxW or BxCxHxW images.
    """
    from torch import as_tensor

    if not inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    mean = as_tensor(mean, dtype=dtype, device=tensor.device)
    std = as_tensor(std, dtype=dtype, device=tensor.device)

    if tensor.dim() == 4:
        tensor.sub_(mean[None, :, None, None]).div_(std[None, :, None, None])
    elif tensor.dim() == 3:
        tensor.sub_(mean[:, None, None]).div_(std[:, None, None])
    else:
        raise NotImplementedError("Only accepts 3D or 4D tensor")

    return tensor


def denormalize(tensor, mean=NORMALIZE_MEAN, std=NORMALIZE_STD, inplace=False):
    """
    Denormalizes image tensor using VGG mean and std.
    Assumes image has [0,1] values.
    Accepts CxHxW or BxCxHxW images.
    """
    from torch import as_tensor

    if not inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    mean = as_tensor(mean, dtype=dtype, device=tensor.device)
    std = as_tensor(std, dtype=dtype, device=tensor.device)

    if tensor.dim() == 4:
        tensor.mul_(std[None, :, None, None]).add_(mean[None, :, None, None])
    elif tensor.dim() == 3:
        tensor.mul_(std[:, None, None]).add_(mean[:, None, None])
    else:
        raise NotImplementedError("Only accepts 3D or 4D tensor")

    return tensor


def normalize_255(tensor, mean=NORMALIZE_MEAN_255, std=NORMALIZE_STD_255, inplace=False):
    """
    Normalizes image tensor using VGG mean and std.
    Assumes image has [0,255] values.
    Accepts CxHxW or BxCxHxW images.
    """
    return normalize(tensor, mean, std, inplace)


def denormalize_255(tensor, mean=NORMALIZE_MEAN_255, std=NORMALIZE_STD_255, inplace=False):
    """
    Denormalizes image tensor using VGG mean and std.
    Assumes image has [0,255] values.
    Accepts CxHxW or BxCxHxW images.
    """
    return denormalize(tensor, mean, std, inplace)


def layernames(features: _T.List[_nn.Module]) -> _T.List[str]:
    """
    Generates a mapping of {layername: index} based on the VGG layers (i.e. features)
    """
    from torch.nn import Conv2d, ReLU, BatchNorm2d, MaxPool2d

    names = []

    n, m = 1, 0
    for layer in features:
        if isinstance(layer, Conv2d):
            m += 1
            names.append("conv{}_{}".format(n, m))
        elif isinstance(layer, ReLU):
            names.append("relu{}_{}".format(n, m))
        elif isinstance(layer, BatchNorm2d):
            names.append("batch{}_{}".format(n, m))
        elif isinstance(layer, MaxPool2d):
            names.append("pool{}".format(n))
            n += 1
            m = 0

    return names


class VggExtractor(_FeatureExtractor):
    """
    Allows extraction of features from specific layers of the VGG network.
    """

    class Features(_nn.Sequential):

        def __init__(self, nlayers: int = 13, bn: bool = False, **kwds):
            model_name = f"vgg{nlayers}{'_bn' if bn else ''}"
            layers = getattr(base, model_name)(**kwds).features
            names = layernames(layers)

            from collections import OrderedDict
            modules = OrderedDict()
            for name, layer in zip(names, layers):
                modules[name] = layer

            super().__init__(modules)

    def __init__(self, targets: _T.List[str], vgg_nlayers: int = 13, vgg_bn: bool = False, pretrained: bool = True, **kwds):
        model = VggExtractor.Features(nlayers=vgg_nlayers, bn=vgg_bn, pretrained=pretrained, **kwds)
        super().__init__(model, targets)


del _T, _nn, _FeatureExtractor
