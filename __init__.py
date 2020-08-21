from . import _internal
if _internal.lazyload_submodules():
    from . import ctx, data, events, features, log, metrics, nn, noise, transforms, dirp, file, lazyloader, runq, search, strf, vgg

from .functional import *

if _internal.lazyload("torch", "torch"):
    import torch
if _internal.lazyload("torchvision", "torchvision"):
    import torchvision
