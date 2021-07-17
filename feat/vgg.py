import typing as _T
import torch as _th
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
        return tensor.sub_(mean[None, :, None, None]).div_(std[None, :, None, None])
    if tensor.dim() == 3:
        return tensor.sub_(mean[:, None, None]).div_(std[:, None, None])

    raise NotImplementedError("Only accepts 3D or 4D tensor")


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
        return tensor.mul_(std[None, :, None, None]).add_(mean[None, :, None, None])
    if tensor.dim() == 3:
        tensor.mul_(std[:, None, None]).add_(mean[:, None, None])

    raise NotImplementedError("Only accepts 3D or 4D tensor")


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


def layernames(features: _T.List[_th.nn.Module]) -> _T.List[str]:
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


class _Lambda(_th.nn.Module):

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def forward(self, *args, **kwds):
        return self.fn(*args, **kwds)


class VggExtractor(_FeatureExtractor):
    """
    Allows extraction of features from specific layers of the VGG network.
    """

    def __init__(
        self,
        targets: _T.List[str],
        vgg_nlayers: int = 13,
        vgg_bn: bool = False,
        inplace_relu: bool = False,
        freeze: bool = False,
        pool: _T.Literal["max", "avg"] = "max",
        preprocess: _T.Callable[[_th.Tensor], _th.Tensor] = normalize,
        final_layer: _T.Union[str, int] = None,
        pretrained: bool = True,
        **kwds
    ):
        # Look for the specific vgg model
        vgg_name = f"vgg{vgg_nlayers}{'_bn' if vgg_bn else ''}"
        vgg_constructor = getattr(base, vgg_name)

        # Extract the feature layers and their corresponding names
        layers = vgg_constructor(pretrained=pretrained, **kwds).features
        names = layernames(layers)

        # Initialize the submodule storage
        from collections import OrderedDict
        modules = OrderedDict()

        # Add the preprocessing layer if provided
        if callable(preprocess):
            preprocess = _Lambda(preprocess)
            modules["preprocess"] = preprocess

        # Perform module-wise processing based on parameters
        for idx, (name, layer) in enumerate(zip(names, layers)):

            # In-place ReLU
            if isinstance(layer, _th.nn.ReLU):
                layer.inplace = inplace_relu

            # Use average pool instead of max pool (useful for style transfer)
            elif isinstance(layer, _th.nn.MaxPool2d):
                if pool == "avg":
                    alt_layer = _th.nn.AvgPool2d(
                        kernel_size=layer.kernel_size,
                        stride=layer.stride,
                        padding=layer.padding
                    )
                    layer = alt_layer

            modules[name] = layer

            # Discard other layers if final_layer is reached
            if name == final_layer or idx == final_layer:
                break

        # Agglomerate the modules
        model = _th.nn.Sequential(modules)

        # Freeze the model if desired
        if freeze:
            for p in model.parameters():
                p.requires_grad = False

        # Initialize feature extractor
        super().__init__(model, targets)


del _T, _th, _FeatureExtractor
