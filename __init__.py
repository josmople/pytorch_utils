from . import _internal
if _internal.lazyload_submodules():
    from . import cfg, data, decorators, dirp, feat, paths, tb

from .dirp import dirpath, ts
