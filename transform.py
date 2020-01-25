class PathToImage:

    @staticmethod
    def default_image_loader(cls, path):
        from PIL.Image import open
        return open(path)

    def __init__(self, loader=default_image_loader):
        self.loader = loader

    def __call__(self, path):
        return self.loader(path)
