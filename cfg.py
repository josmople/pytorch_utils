import typing as _T
import argparse as _argparse


class Params:

    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds

    def __str__(self):
        args = ", ".join(self.args)
        kwds = ", ".join(f"{k}={v!r}" for k, v in self.kwds.items())
        params = ", ".join([args, kwds])
        return f"{self.__class__.__name__}({params})"


class ParseArgsDescriptor(Params):

    @staticmethod
    def namespace(obj, val=None) -> _argparse.Namespace:
        if val is None:
            for name in vars(obj):
                if name == "__namespace_attr":
                    return getattr(obj, "__namespace_attr")
            return None

        setattr(obj, "__namespace_attr", val)
        return val

    @staticmethod
    def generate_parser(obj) -> _argparse.ArgumentParser:
        if isinstance(obj, _argparse.ArgumentParser):
            from copy import deepcopy
            return deepcopy(obj)
        if isinstance(obj, type) and issubclass(obj, _argparse.ArgumentParser):
            return obj()
        return _argparse.ArgumentParser()

    @staticmethod
    def apply_parser_arguments(parser: _argparse.ArgumentParser, config: object) -> _argparse.ArgumentParser:
        from inspect import getattr_static
        for key in dir(config):
            val = getattr_static(config, key)
            if isinstance(val, Params):
                if isinstance(val, ParseArgsDescriptor):
                    val.name = key
                if len(val.args) != 0 and len(val.kwds) != 0:  # Empty Params will just be an accessor
                    parser.add_argument(*val.args, **val.kwds)
        return parser

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.name = None

    def __get__(self, obj, objtype=None):
        if obj is None:
            obj = objtype

        namespace = self.namespace(obj)
        if namespace is None:

            parser = self.generate_parser(obj)
            parser = self.apply_parser_arguments(parser, config=objtype)

            namespace = parser.parse_args()
            self.namespace(obj, namespace)

        return getattr(namespace, self.name)

    def __str__(self):
        args = ", ".join(self.args)
        kwds = ", ".join(f"{k}={v!r}" for k, v in self.kwds.items())
        params = ", ".join([args, kwds])
        return f"{self.name}={self.__class__.__name__}({params})"


def arg(
        *name_or_flags: str,
        action: _T.Union[str, _T.Type[_argparse.Action]] = ...,
        nargs: _T.Union[int, str] = ...,
        const: _T.Any = ...,
        default: _T.Any = ...,
        type: _T.Union[_T.Callable[[str], _T.Any], _argparse.FileType] = ...,
        choices: _T.Iterable = ...,
        required: bool = ...,
        help: str = ...,
        metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
        dest: str = ...,
        version: str = ...,
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

    return ParseArgsDescriptor(*name_or_flags, **arg_kwds)
