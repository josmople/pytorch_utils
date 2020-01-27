from .img import pil_loader as _default_image_loader


class PathToImage:

    def __init__(self, loader=_default_image_loader):
        self.loader = loader

    def __call__(self, path):
        return self.loader(path)
