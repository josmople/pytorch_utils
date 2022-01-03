from .lazy import lazyload as _lazyload, DUMMY_TRUE as _DUMMY_TRUE

from torchvision.transforms import *

functional = _lazyload("torchvision.transforms.functional")
if _DUMMY_TRUE:
    import torchvision.transforms.functional as functional


del _lazyload
