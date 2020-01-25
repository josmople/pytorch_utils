from PIL import Image


class PathToImage:

    def __init__(self, loader=Image.open):
        self.loader = loader

    def __call__(self, path):
        return self.loader(path)
