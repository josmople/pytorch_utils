from torch.nn import Module as _Module

import torchvision.models.vgg as models

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


def normalize_255(tensor, mean=NORMALIZE_MEAN_255, std=NORMALIZE_STD_255, inplace=False):
    """
    Normalizes image tensor using VGG mean and std.

    Assumes image has [0,255] values.

    Accepts CxHxW or BxCxHxW images.
    """
    return normalize(tensor, mean, std, inplace)


class VGGExtractor(_Module):

    @staticmethod
    def layername_index_mapping(features):
        """
        Generates a mapping of {layername: index} based on the VGG layers (i.e. features)
        """
        from torch.nn import Conv2d, ReLU, BatchNorm2d, MaxPool2d

        mapping = {}

        n, m = 1, 0
        for i, layer in enumerate(features):
            if isinstance(layer, Conv2d):
                m += 1
                mapping["conv{}_{}".format(n, m)] = i
            elif isinstance(layer, ReLU):
                mapping["relu{}_{}".format(n, m)] = i
            elif isinstance(layer, BatchNorm2d):
                mapping["batch{}_{}".format(n, m)] = i
            elif isinstance(layer, MaxPool2d):
                mapping["pool{}".format(n)] = i
                n += 1
                m = 0

        return mapping

    @staticmethod
    def fetches_to_idxs(fetches, mapping):
        """
        Turns a List[Union[str, int]] to List[int]

        int values in fetches refers to layer index
        str values in fetches refers to layer name (see self.layernames or mapping)

        Special indexes
        -1 -> corresponds to model input
        None -> corresponds to post-normalization, if there is no normalization has similar output to -1
        """
        idxs = []
        for idx in fetches:
            if isinstance(idx, int) or idx is None:
                idxs.append(idx)
            elif isinstance(idx, str):
                try:
                    idx = mapping[idx]
                except:
                    raise ValueError("Layer `{}` not found".format(idx))
                idxs.append(idx)
            else:
                raise ValueError("Expected `fetches` to be list[int], list[str]")
        return idxs

    def __init__(self, vgg_nlayer=19, vgg_bn=False, requires_grad=False, inplace_relu=False, max_layer=None, normalize_fn=None, **kwargs):
        super().__init__()

        assert isinstance(vgg_nlayer, (int, str))
        assert isinstance(vgg_bn, bool)
        assert isinstance(requires_grad, bool)
        assert isinstance(inplace_relu, bool)
        assert callable(normalize_fn) or normalize_fn is None

        model_name = f"vgg{vgg_nlayer}{'_bn' if vgg_bn else ''}"
        self.model = getattr(models, model_name)(**kwargs).features
        self.mapping = self.__class__.layername_index_mapping(self.model)
        self.normalize = normalize_fn

        max_idx = (self.mapping[str(max_layer)] + 1) if isinstance(max_layer, str) else max_layer
        self.model = self.model[:max_idx]

        for param in self.model.parameters():
            param.requires_grad_(requires_grad)

        from torch.nn import ReLU
        for layer in self.model:
            if isinstance(layer, ReLU):
                layer.inplace = inplace_relu

    @property
    def layernames(self):
        return list(self.mapping.keys())

    @property
    def layernames_valid(self):
        return self.layernames[:len(self.model)]

    @property
    def fetchlist(self):
        out = [-1, *range(len(self.model)), *self.layernames_valid]
        if self.normalize is not None:
            out.append(None)
        return out

    def forward(self, x, fetches=None):
        if fetches is None:
            return self.model(x)
        if isinstance(fetches, (int, str)):
            fetches = [fetches]
            fetches = self.__class__.fetches_to_idxs(fetches, self.mapping)
            return self._forward(x, fetches)[0]
        if isinstance(fetches, (tuple, list)):
            fetches = self.__class__.fetches_to_idxs(fetches, self.mapping)
            return self._forward(x, fetches)
        raise ValueError("Expected `fetches` to be int, str, list[int], list[str]")

    def _forward(self, x, idxs):
        assert isinstance(idxs, (list, tuple))
        assert all([isinstance(idx, int) for idx in idxs])
        assert all([idx >= -2 for idx in idxs])

        outputs = {}

        y = x
        if -1 in idxs:
            outputs[-1] = y

        if self.normalize is not None:
            y = self.normalize(y)
        if None in idxs:
            outputs[None] = y

        last_idxs = max(idxs)

        for idx, layer in enumerate(self.model):
            y = layer(y)

            if idx in idxs:
                outputs[idx] = y

            if idx > last_idxs:
                break

        return [outputs[idx] for idx in idxs]


del _Module
