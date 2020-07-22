from ..lazyloader import LazyLoader as _LL

tfboard = _LL("tfboard", globals(), "pytorch_utils.log.tfboard")
pytorch = _LL("pytorch", globals(), "pytorch_utils.log.pytorch")

import decorator


def pytorch_logger(rootdir):
    from .pytorch import PyTorchLogger
    return PyTorchLogger(rootdir)


del _LL
