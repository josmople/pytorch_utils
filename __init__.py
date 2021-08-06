from . import lazy
if lazy.lazyload_submodules():
    from . import az, cfg, data, dirp, fn, iz, feat, paths, resize, tb

from .dirp import dirpath, ts
