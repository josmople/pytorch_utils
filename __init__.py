from .lazy import lazyload_submodules as _lazyload_submodules
if _lazyload_submodules():
    from . import az, cfg, data, dirp, fn, lazy, log, iz, feat, paths, resize, strf, t
