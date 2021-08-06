from types import ModuleType as _ModuleType


class LazyLoader(_ModuleType):
    """
    Lazily import a module, mainly to avoid pulling in large dependencies.

    `contrib`, and `ffmpeg` are examples of modules that are large and not always
    needed, and this allows them to only be loaded when they are used.

    Code copied from https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/util/lazy_loader.py
    """

    # The lint error here is incorrect.
    def __init__(self, local_name, parent_module_globals, name):  # pylint: disable=super-on-old-class
        self._local_name = local_name
        self._parent_module_globals = parent_module_globals

        super(LazyLoader, self).__init__(name)

    def _load(self):
        from importlib import import_module

        # Import the target module and insert it into the parent's namespace
        module = import_module(self.__name__)
        self._parent_module_globals[self._local_name] = module

        # Update this object's dict so that if someone keeps a reference to the LazyLoader,
        # lookups are efficient (__getattr__ is only called on lookups that fail).
        self.__dict__.update(module.__dict__)

        return module

    def __getattr__(self, item):
        module = self._load()
        return getattr(module, item)

    def __dir__(self):
        module = self._load()
        return dir(module)


def lazyload(localname, name=None, module_globals=None):
    if name is None:
        name = localname
    if module_globals is None:
        from sys import _getframe
        module_globals = _getframe(1).f_globals

    ll = LazyLoader(localname, module_globals, name)
    module_globals[localname] = ll
    return False


def lazyload_submodules(root_modname=None, include_submodules=None, exclude_submodules=None, stack_idx=1) -> True:
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

    # Put the function call in an if statement for intellisense
    # See example below
    # ```
    # # <Actual> return value is False, but <Annotation> says True
    # if load_lazy_submodules():
    #     # Will be registered by intellisense due to <Annotation=True>
    #     # But not actually loaded due to return value <Actual=False>
    #     from . import submodule
    # ```
    return eval("not not not not not 1", {}, {})
