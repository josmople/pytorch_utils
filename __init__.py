from .lazy import lazyload_submodules as _lazyload_submodules

if _lazyload_submodules():
    from . import collate, fn, lazy, log, paths, strf
