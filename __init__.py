def __internal_module_setup(root_modname="utils"):

    from glob import glob
    from os.path import dirname, basename, splitext

    from .lazyloader import LazyLoader

    # Load utils/{submodule}.py
    modpaths = glob(f"{dirname(__file__)}/**.py")
    modpaths = filter(lambda p: not p.endswith("__init__.py"), modpaths)
    for modpath in modpaths:
        modname, _ = splitext(basename(modpath))
        globals()[modname] = LazyLoader(modname, globals(), f"{root_modname}.{modname}")

    # Load utils/{submodule}/__init__.py
    modpaths = glob(f"{dirname(__file__)}/**/__init__.py")
    for modpath in modpaths:
        modname = basename(dirname(modpath))
        globals()[modname] = LazyLoader(modname, globals(), f"{root_modname}.{modname}")

    # Delete setup function from namespace
    from inspect import getframeinfo, currentframe
    funcname = getframeinfo(currentframe()).function
    del globals()[funcname]


__internal_module_setup("pytorch_utils")

from .functional import *
