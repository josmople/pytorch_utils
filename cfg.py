import typing as _T
import argparse


class ParseArgsDescriptor:

    @staticmethod
    def get_namespace(obj: object, objtype: type) -> argparse.Namespace:
        src = obj or objtype

        keys1 = getattr(src, "__dict__", {}).keys()
        keys2 = getattr(src, "__slots__", [])

        for name in [*keys1, *keys2]:
            if name == "__namespace__":
                return getattr(src, "__namespace__")
        return None

    @staticmethod
    def set_namespace(obj: object, objtype: type, val: argparse.Namespace):
        src = obj or objtype
        setattr(src, "__namespace__", val)

    @staticmethod
    def generate_parser(obj: object, objtype: type) -> argparse.ArgumentParser:
        from inspect import getattr_static

        if isinstance(obj, argparse.ArgumentParser):
            from copy import deepcopy
            parser = deepcopy(obj)
        elif issubclass(objtype, argparse.ArgumentParser):
            parser = objtype()
        else:
            parser = argparse.ArgumentParser()

        # Apply parser arguments
        config = obj or objtype

        for key in dir(config):
            val = getattr_static(config, key)
            if isinstance(val, ParseArgsDescriptor):
                if val.name is None:
                    val.name = key
                if len(val.args) != 0 and len(val.kwds) != 0:  # Empty Params will just be an accessor
                    parser.add_argument(*val.args, **val.kwds)
        return parser

    @staticmethod
    def generate_namespace(obj: object, objtype: type, parser: argparse.ArgumentParser):
        src = obj or objtype
        custom_parameters = getattr(src, "__parameters__", None)
        if custom_parameters is None:
            return parser.parse_args()
        return parser.parse_args(custom_parameters)

    def namespace(self, obj: object, objtype: type):
        namespace = self.get_namespace(obj, objtype)

        if namespace is None:
            parser = self.generate_parser(obj, objtype)
            raw_namespace = self.generate_namespace(obj, objtype, parser)

            self.set_namespace(obj, objtype, raw_namespace)
            namespace = self.get_namespace(obj, objtype)

        return namespace

    def attribute(self, namespace):
        return getattr(namespace, self.name)

    def __init__(self, name: str = None, args: list = None, kwds: dict = None):
        self.name = name
        self.args = args or []
        self.kwds = kwds or {}

    def __get__(self, obj: object, objtype: type = None):
        namespace = self.namespace(obj, objtype)
        return self.attribute(namespace)

    def __set__(self, obj, value):
        print(obj, value)

    def __str__(self):
        args = ", ".join([f"{v!r}" for v in self.args])
        kwds = ", ".join(f"{k}={v!r}" for k, v in self.kwds.items())
        params = ", ".join([args, kwds])
        return f"{self.name}={self.__class__.__name__}({params})"


def arg(
        *name_or_flags: str,
        action: _T.Union[str, _T.Type[argparse.Action]] = ...,
        nargs: _T.Union[int, str] = ...,
        const: _T.Any = ...,
        default: _T.Any = ...,
        type: _T.Union[_T.Callable[[str], _T.Any], argparse.FileType] = ...,
        choices: _T.Iterable = ...,
        required: bool = ...,
        help: str = ...,
        metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
        dest: str = ...,
        version: str = ...,
        namespace_attr_name=None,
        **kwargs: _T.Any
):
    arg_kwds = {}
    if action != ...:
        arg_kwds["action"] = action
    if nargs != ...:
        arg_kwds["nargs"] = nargs
    if const != ...:
        arg_kwds["const"] = const
    if default != ...:
        arg_kwds["default"] = default
    if type != ...:
        arg_kwds["type"] = type
    if choices != ...:
        arg_kwds["choices"] = choices
    if required != ...:
        arg_kwds["required"] = required
    if help != ...:
        arg_kwds["help"] = help
    if metavar != ...:
        arg_kwds["metavar"] = metavar
    if dest != ...:
        arg_kwds["dest"] = dest
    if version != ...:
        arg_kwds["version"] = version

    arg_kwds = {**arg_kwds, **kwargs}

    return ParseArgsDescriptor(name=namespace_attr_name, args=name_or_flags, kwds=arg_kwds)
