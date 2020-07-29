from torch.nn import Module as _Module

import torchvision.models.vgg as models

NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]


def normalize(tensor, mean=NORMALIZE_MEAN, std=NORMALIZE_STD, inplace=False):
    from torchvision.transforms.functional import normalize
    if tensor.dim() == 3:
        return normalize(tensor, mean=mean, std=std, inplace=inplace)
    if tensor.dim() == 4:
        if not inplace:
            tensor = tensor.clone()
        dtype = tensor.dtype
        mean = torch.as_tensor(mean, dtype=dtype, device=tensor.device)
        std = torch.as_tensor(std, dtype=dtype, device=tensor.device)
        tensor.sub_(mean[None, :, None, None]).div_(std[None, :, None, None])
        return tensor
    raise NotImplementedError("Only accepts 3D or 4D tensor")


class VGGExtractor(_Module):

    @staticmethod
    def layername_index_mapping(features):
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
        idxs = []
        for idx in fetches:
            if isinstance(idx, int):
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

    def __init__(self, vgg_nlayer=19, vgg_bn=False, requires_grad=False, inplace_relu=False, **kwargs):
        super().__init__()

        assert isinstance(vgg_nlayer, (int, str))
        assert isinstance(vgg_bn, bool)
        assert isinstance(requires_grad, bool)
        assert isinstance(inplace_relu, bool)

        model_name = f"vgg{vgg_nlayer}{'_bn' if vgg_bn else ''}"
        self.model = getattr(models, model_name)(**kwargs).features
        self.mapping = self.__class__.layername_index_mapping(self.model)

        for param in self.model.parameters():
            param.requires_grad_(requires_grad)

        from torch.nn import ReLU
        for layer in self.model:
            if isinstance(layer, ReLU):
                layer.inplace = inplace_relu

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

        last_idxs = max(idxs)

        for idx, layer in enumerate(self.model):
            y = layer(y)

            if idx in idxs:
                outputs[idx] = y

            if idx > last_idxs:
                break

        return [outputs[idx] for idx in idxs]


del _Module
