from ..lazyloader import LazyLoader as _LL

tfboard = _LL("tfboard", globals(), "pytorch_utils.log.tfboard")
pytorch = _LL("pytorch", globals(), "pytorch_utils.log.pytorch")

from . import decorator

del _LL
