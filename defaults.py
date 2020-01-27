
def image_loader(path):
    from PIL.Image import open
    return open(path)


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
