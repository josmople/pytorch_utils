import torch.nn as nn
import torchvision.models.vgg as vgg


def vgg_normalize(tensor):
    from .functional import normalize
    return normalize(
        tensor,
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )


def vgg_denormalize(tensor):
    from .functional import denormalize
    return denormalize(
        tensor,
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )


class VGGExtractor(nn.Module):

    @staticmethod
    def layername_index_mapping(features):
        mapping = {}

        n, m = 1, 0
        for i, layer in enumerate(features):
            if isinstance(layer, nn.Conv2d):
                m += 1
                mapping["conv{}_{}".format(n, m)] = i
            elif isinstance(layer, nn.ReLU):
                mapping["relu{}_{}".format(n, m)] = i
            elif isinstance(layer, nn.BatchNorm2d):
                mapping["batch{}_{}".format(n, m)] = i
            elif isinstance(layer, nn.MaxPool2d):
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

    def __init__(self, vgg_nlayer=19, vgg_bn=False, requires_grad=False, inplace_relu=False, preprocess=vgg_normalize, **kwargs):
        super().__init__()

        assert isinstance(vgg_nlayer, (int, str))
        assert isinstance(vgg_bn, bool)
        assert isinstance(requires_grad, bool)
        assert isinstance(inplace_relu, bool)
        assert preprocess is None or callable(preprocess)

        model_name = "vgg{}{}".format(vgg_nlayer, "_bn" if vgg_bn else "")
        self.model = getattr(vgg, model_name)(**kwargs).features
        self.mapping = self.__class__.layername_index_mapping(self.model)

        self.preprocess = preprocess
        if self.preprocess is None:
            self.preprocess = lambda x: x

        for param in self.model.parameters():
            param.requires_grad_(requires_grad)

        for layer in self.model:
            if isinstance(layer, nn.ReLU):
                layer.inplace = inplace_relu

    def forward(self, x, fetches=None):
        if fetches is None:
            return self.model(x)
        if isinstance(fetches, (int, str)):
            fetches = [fetches]
            fetches = self.__class__.fetches_to_idxs(fetches, self.mapping)
            return self.forward0(x, fetches)[0]
        if isinstance(fetches, (tuple, list)):
            fetches = self.__class__.fetches_to_idxs(fetches, self.mapping)
            return self.forward0(x, fetches)
        raise ValueError("Expected `fetches` to be int, str, list[int], list[str]")

    def forward0(self, x, idxs):
        assert isinstance(idxs, (list, tuple))
        assert all([isinstance(idx, int) for idx in idxs])
        assert all([idx >= -2 for idx in idxs])

        outputs = {}

        if -2 in idxs:
            outputs[-2] = x

        y = self.preprocess(x)

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
