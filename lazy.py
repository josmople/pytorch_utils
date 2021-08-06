from types import ModuleType as _ModuleType


class LazyLoader(_ModuleType):
    """
    Lazily import a module, mainly to avoid pulling in large dependencies.

    Code copied from https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/util/lazy_loader.py
    """

    def __init__(self, name, parent_module_globals):
        self._parent_module_globals = parent_module_globals
        self._module_cache = None

        super().__init__(name)

    @property
    def _module(self):
        if self._module_cache is not None:
            return self._module_cache

        from importlib import import_module

        # Import the target module and insert it into the parent's namespace
        module = import_module(self.__name__)

        # Find the name of this object (LazyLoader) in the parent's namespace
        # Then insert the actual module in place of this object (LazyLoader)
        for local_name, value in self._parent_module_globals.items():
            if id(value) == id(self):
                self._parent_module_globals[local_name] = module  # Replace
                break

        # Update this object's dict so that if someone keeps a reference to the LazyLoader,
        # lookups are efficient (__getattr__ is only called on lookups that fail).
        self.__dict__.update(module.__dict__)

        # Store then return the value
        self._module_cache = module
        return module

    def __call__(self, *args, **kwds):
        return self._module(*args, **kwds)

    def __getattr__(self, item):
        return getattr(self._module, item)

    def __dir__(self):
        return dir(self._module)


def lazyload(name, module_globals=None):
    if module_globals is None:
        from sys import _getframe
        module_globals = _getframe(1).f_globals
    return LazyLoader(name, module_globals)


def lazyload_submodules(root_module_globals=None, root_module_name=None, include_submodules=None, exclude_submodules=None) -> True:
    """
    Searches all possible submodules (relative to the root module) and makes them lazily-loaded.

    Args:
        root_module_globals: defaults to ``sys._getframe(1).f_globals`` (i.e. ``globals()`` of the caller).
        root_module_name: defaults to ``__package__``.
        include_submodules: if not ``None``, will reject not in the list.
        exclude_submodules: if not ``None``, will reject in the list.
        stack_idx: frame references stack (1 -> the scope of the package/code that called this function).

    Returns:
        The boolean value False. But it is annotated as True. This action is performed to fool Intellisense.

    >>> if lazyload_submodules(): # Annotated to have `True` return type
    >>>     # Statements inside this block is recorded by Intellisense for auto-completion
    >>>     from . import submodule # <- Will not actually run since actual return value is `False`
    """

    from sys import _getframe
    from glob import glob
    from os.path import dirname, basename, splitext

    variables = root_module_globals or _getframe(1).f_globals
    filepath = variables["__file__"]
    root_module_name = root_module_name or variables["__package__"]

    # Load utils/{submodule}.py
    file_submodules = glob(f"{dirname(filepath)}/**.py")
    file_submodules = filter(lambda p: not p.endswith("__init__.py"), file_submodules)
    file_submodules = map(lambda p: splitext(basename(p))[0], file_submodules)

    # Load utils/{submodule}/__init__.py
    dir_submodules = glob(f"{dirname(filepath)}/**/__init__.py")
    dir_submodules = map(lambda p: basename(dirname(p)), dir_submodules)

    # All submodule names
    submodules = list(file_submodules) + list(dir_submodules)

    # Perform filter
    if include_submodules is not None:
        submodules = filter(lambda n: n in include_submodules, submodules)
    if exclude_submodules is not None:
        submodules = filter(lambda n: n not in exclude_submodules, submodules)

    # Assign to parent namespace
    for submodule_name in submodules:
        variables[submodule_name] = LazyLoader(f"{root_module_name}.{submodule_name}", variables)

    # Put the function call in an if statement for Intellisense
    return eval("not not not not not 1", {}, {})
