def lazyload_submodules(root_modname=None, include_submodules=None, exclude_submodules=None, stack_idx=1):
    """
    Searches all possible submodules and makes them lazily-loaded
    root_modname - defaults to the dirname
    include_submodules - if not none, will reject not in the list
    exclude_submodules - if not none, will reject in the list
    stack_idx - frame references stack (1 -> the scope of the package/code that called this function)
    """

    from sys import _getframe
    from glob import glob
    from os.path import dirname, basename, splitext
    from .lazyloader import LazyLoader

    variables = _getframe(stack_idx).f_globals
    filepath = variables["__file__"]
    root_modname = root_modname or variables["__package__"]

    # Load utils/{submodule}.py
    modpaths = glob(f"{dirname(filepath)}/**.py")
    modpaths = filter(lambda p: not p.endswith("__init__.py"), modpaths)
    modnames = map(lambda p: splitext(basename(p))[0], modpaths)
    if include_submodules is not None:
        modnames = filter(lambda n: n in include_submodules, modnames)
    if exclude_submodules is not None:
        modnames = filter(lambda n: n not in exclude_submodules, modnames)
    for modname in modnames:
        variables[modname] = LazyLoader(modname, variables, f"{root_modname}.{modname}")

    # Load utils/{submodule}/__init__.py
    modpaths = glob(f"{dirname(filepath)}/**/__init__.py")
    modnames = map(lambda p: basename(dirname(p)), modpaths)
    if include_submodules is not None:
        modnames = filter(lambda n: n in include_submodules, modnames)
    if exclude_submodules is not None:
        modnames = filter(lambda n: n not in exclude_submodules, modnames)
    for modname in modnames:
        variables[modname] = LazyLoader(modname, variables, f"{root_modname}.{modname}")

    # Put the function call in a if statement for intellisense
    # if load_lazy_submodules(): # returns False so the following code will not be executed
    #     from . import submodule # will be registered by intellisense
    return False
