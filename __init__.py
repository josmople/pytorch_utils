from .lazy import lazyload_submodules as _lazyload_submodules
if _lazyload_submodules():
    from . import az, cfg, collate, data, dirp, fn, im, io, lazy, log, iz, feat, paths, resize, strf, tags, tvision
