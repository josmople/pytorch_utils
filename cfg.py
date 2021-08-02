import typing as _T
import argparse


class utils:

    @staticmethod
    def get_namespace(src: object, namespace_attr="__namespace__") -> argparse.Namespace:
        keys1 = getattr(src, "__dict__", {}).keys()
        keys2 = getattr(src, "__slots__", [])

        for name in [*keys1, *keys2]:
            if name == namespace_attr:
                return getattr(src, namespace_attr)

        return None

    @staticmethod
    def set_namespace(src: object, val: argparse.Namespace, namespace_attr="__namespace__"):
        setattr(src, namespace_attr, val)

    @staticmethod
    def create_parser_instance(config: object) -> argparse.ArgumentParser:
        if isinstance(config, type):
            if issubclass(config, argparse.ArgumentParser):
                return config()

        if isinstance(config, argparse.ArgumentParser):
            from copy import deepcopy
            return deepcopy(config)

        return argparse.ArgumentParser()

    @staticmethod
    def apply_parser_config(parser: argparse.ArgumentParser, config: object) -> argparse.ArgumentParser:
        from inspect import getattr_static

        for key in dir(config):
            val = getattr_static(config, key)
            if isinstance(val, ParseArgsDescriptor):
                if val.name is None:
                    val.name = key
                if len(val.args) != 0 and len(val.kwds) != 0:  # Empty Params will just be an accessor
                    parser.add_argument(*val.args, **val.kwds)
        return parser

    @staticmethod
    def parse_args(parser: argparse.ArgumentParser, config: object, parameter_attr="__parameters__") -> argparse.Namespace:
        custom_parameters = getattr(config, parameter_attr, None)
        if custom_parameters is None:
            return parser.parse_args()
        if isinstance(custom_parameters, str):
            custom_parameters = utils.split_command(custom_parameters)
        return parser.parse_args(custom_parameters)

    @staticmethod
    def split_command(cmd) -> _T.List[str]:
        """
        Like `shlex.split`, but uses the Windows splitting syntax when run on Windows.

        From: https://stackoverflow.com/a/54730743
        """

        import subprocess
        import sys
        import json

        if not cmd:
            return []
        full_cmd = '{} {}'.format(
            subprocess.list2cmdline([sys.executable, '-c', 'import sys, json; print(json.dumps(sys.argv[1:]))']),
            cmd
        )
        ret = subprocess.check_output(full_cmd).decode()
        return json.loads(ret)


class ParseArgsDescriptor:

    @staticmethod
    def get_namespace(obj: object, objtype: type) -> argparse.Namespace:
        src = obj or objtype
        return utils.get_namespace(src)

    @staticmethod
    def set_namespace(obj: object, objtype: type, val: argparse.Namespace):
        src = obj or objtype
        utils.set_namespace(src, val)

    @staticmethod
    def create_parser(obj: object, objtype: type) -> argparse.ArgumentParser:
        config = obj or objtype
        parser = utils.create_parser_instance(config)
        return utils.apply_parser_config(parser, config)

    @staticmethod
    def create_namespace(obj: object, objtype: type, parser: argparse.ArgumentParser):
        config = obj or objtype
        return utils.parse_args(parser, config)

    def namespace(self, obj: object, objtype: type):
        namespace = self.get_namespace(obj, objtype)

        if namespace is None:
            parser = self.create_parser(obj, objtype)
            raw_namespace = self.create_namespace(obj, objtype, parser)

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

    def __str__(self):
        args = ", ".join([f"{v!r}" for v in self.args])
        kwds = ", ".join(f"{k}={v!r}" for k, v in self.kwds.items())
        params = ", ".join([args, kwds])
        return f"{self.name}={self.__class__.__name__}({params})"


DEFAULT = _T.TypeVar("DEFAULT")


@_T.overload
def arg(
    *name_or_flags: str,
    action: _T.Union[str, _T.Type[argparse.Action]] = ...,
    nargs: _T.Union[int, _T.Literal["*", "+"]],
    const: _T.Any = ...,
    default: DEFAULT = ...,
    type: _T.Union[_T.Type[DEFAULT], argparse.FileType] = ...,
    choices: _T.Iterable[DEFAULT] = ...,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attr_name=None,
    **kwargs: _T.Any
) -> _T.List[DEFAULT]: ...


@_T.overload
def arg(
    *name_or_flags: str,
    action: _T.Union[str, _T.Type[argparse.Action]] = ...,
    nargs: _T.Literal["?"],
    const: _T.Any = ...,
    default: DEFAULT = ...,
    type: _T.Union[_T.Type[DEFAULT], argparse.FileType] = ...,
    choices: _T.Iterable[DEFAULT] = ...,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attr_name=None,
    **kwargs: _T.Any
) -> DEFAULT: ...


@_T.overload
def arg(
    *name_or_flags: str,
    action: _T.Union[str, _T.Type[argparse.Action]] = ...,
    const: _T.Any = ...,
    default: DEFAULT = ...,
    type: _T.Union[_T.Type[DEFAULT], argparse.FileType] = ...,
    choices: _T.Iterable[DEFAULT] = ...,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attr_name=None,
    **kwargs: _T.Any
) -> DEFAULT: ...


@_T.overload
def arg(
    *name_or_flags: str,
    nargs: _T.Literal["+"],
    action: _T.Union[str, _T.Type[argparse.Action]] = ...,
    const: _T.Any = ...,
    default: DEFAULT = ...,
    type: _T.Union[_T.Type[DEFAULT], argparse.FileType] = ...,
    choices: _T.Iterable[DEFAULT] = ...,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attr_name=None,
    **kwargs: _T.Any
) -> DEFAULT: ...


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
