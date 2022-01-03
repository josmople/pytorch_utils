from .lazy import lazyload as _lazyload, DUMMY_TRUE as _DUMMY_TRUE

vision = _lazyload("torchvision.transforms")
audio = _lazyload("torchaudio.transforms")


class F:
    vision = _lazyload("torchvision.transforms.functional")

    if _DUMMY_TRUE:
        import torchvision.transforms.functional as vision


if _DUMMY_TRUE:
    import torchvision.transforms as vision
    import torchaudio.transforms as audio


del _lazyload
