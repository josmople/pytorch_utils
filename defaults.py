
def image_loader(path):
    from PIL.Image import open
    return open(path)


def vgg_normalize():
    from torchvision.transforms import Normalize
    return Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
