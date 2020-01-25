from .defaults import image_loader


class PathToImage:

    def __init__(self, loader=image_loader):
        self.loader = loader

    def __call__(self, path):
        return self.loader(path)
