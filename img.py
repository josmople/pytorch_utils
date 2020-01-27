def pil_loader(path):
    from PIL.Image import open
    return open(str(path))


RESAMPLE = {
    "NEAREST": 0,
    "NONE": 0,
    "BOX": 4,
    "BILINEAR": 2,
    "LINEAR": 2,
    "HAMMING": 5,
    "BICUBIC": 3,
    "CUBIC": 3,
    "LANCZOS": 1,
    "ANTIALIAS": 1,
}


def pil_resize_scale(img, scale, resample="nearest"):
    from PIL.Image import Image
    from .check import is_number_or_pair

    assert isinstance(img, Image)

    resample = str(resample).upper()
    assert resample in RESAMPLE
    resample = RESAMPLE[resample]

    SH, SW = is_number_or_pair(scale)

    W, H = img.size
    NW, NH = int(SW * W), int(SH * H)

    return img.resize(size=(NW, NH), resample=resample)
