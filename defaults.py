
def image_loader(path):
    from PIL.Image import open
    return open(path)


def vgg_normalize(tensor):
    from torchvision.transforms.functional import normalize
    return normalize(
        tensor,
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )


def vgg_denormalize():
    from torchvision.transforms.functional import normalize
    return normalize(
        tensor,
        mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
        std=[1/0.229, 1/0.224, 1/0.225]
    )


def logdir(dirpath="logs/{start_ts}", **configs):
    from .log import LogDir, timestamp

    start_ts = timestamp()

    def default_meta():
        meta = {
            'start_ts': start_ts,
            'ts': timestamp(),
        }
        for key in configs:
            val = configs[key]
            if callable(val):
                val = val()
            meta[key] = val
        return meta

    return LogDir(
        dirpath.format(**default_meta()),
        default_prepare=True,
        default_meta=default_meta
    )
