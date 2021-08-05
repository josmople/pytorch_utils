from . import _internal
if _internal.lazyload_submodules():
    from . import az, cfg, data, decorators, dirp, iz, feat, paths, tb

from .dirp import dirpath, ts
