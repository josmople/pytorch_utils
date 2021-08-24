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
    def copy_parser(base: object) -> argparse.ArgumentParser:
        if isinstance(base, type):
            if issubclass(base, argparse.ArgumentParser):
                return base()

        if isinstance(base, argparse.ArgumentParser):
            from copy import deepcopy
            return deepcopy(base)

        return argparse.ArgumentParser()

    @staticmethod
    def apply_config(parser: argparse.ArgumentParser, config: object) -> argparse.ArgumentParser:
        from inspect import getattr_static

        for key in dir(config):
            val = getattr_static(config, key)
            if isinstance(val, ParseArgsDescriptor):
                if val.name is None:
                    val.name = key
                args = val.args
                kwds = val.kwds

                if "is_key_args" in val.meta and val.meta["is_key_args"]:
                    args = (f"--{key}", *args)

                if len(args) != 0 and len(kwds) != 0:  # Empty Params will just be an accessor
                    parser.add_argument(*args, **kwds)
        return parser

    @staticmethod
    def create_parser(config):
        parser = utils.copy_parser(config)
        parser = utils.apply_config(parser, config)
        return parser

    @staticmethod
    def create_namespace(parser: argparse.ArgumentParser, config: object, parameter_attr="__parameters__") -> argparse.Namespace:
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

    def get_namespace(self, obj: object, objtype: type) -> argparse.Namespace:
        src = obj or objtype
        return utils.get_namespace(src)

    def set_namespace(self, obj: object, objtype: type, val: argparse.Namespace):
        src = obj or objtype
        utils.set_namespace(src, val)

    def create_parser(self, obj: object, objtype: type) -> argparse.ArgumentParser:
        config = obj or objtype
        return utils.create_parser(config)

    def create_namespace(self, obj: object, objtype: type, parser: argparse.ArgumentParser):
        config = obj or objtype
        return utils.create_namespace(parser, config)

    def namespace(self, obj: object, objtype: type):
        namespace = self.get_namespace(obj, objtype)

        if not namespace:
            parser = self.create_parser(obj, objtype)
            raw_namespace = self.create_namespace(obj, objtype, parser)

            self.set_namespace(obj, objtype, raw_namespace)
            namespace = self.get_namespace(obj, objtype)

        return namespace

    def attribute(self, namespace):
        return getattr(namespace, self.name)

    def __init__(self, name: str = None, args: list = None, kwds: dict = None, meta: dict = None):
        self.name = name
        self.args = args or []
        self.kwds = kwds or {}
        self.meta = meta or {}

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
    default: _T.List[DEFAULT] = ...,
    type: _T.Union[_T.Type[DEFAULT], argparse.FileType] = ...,
    choices: _T.Iterable[DEFAULT] = ...,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attrname=None,
    attrname_as_parsename=True,
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
    namespace_attrname=None,
    attrname_as_parsename=True,
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
    namespace_attrname=None,
    attrname_as_parsename=True,
    **kwargs: _T.Any
) -> DEFAULT: ...


@_T.overload
def arg(
    *name_or_flags: str,
    action="store_true",
    default=False,
    type=bool,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attrname=None,
    attrname_as_parsename=True,
    **kwargs: _T.Any
) -> bool: ...


@_T.overload
def arg(
    *name_or_flags: str,
    action="store_false",
    default=True,
    type=bool,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attrname=None,
    attrname_as_parsename=True,
    **kwargs: _T.Any
) -> bool: ...


@_T.overload
def arg(
    *name_or_flags: str,
    action="store_const",
    const: DEFAULT = ...,
    type: _T.Type[DEFAULT] = ...,
    required: bool = ...,
    help: str = ...,
    metavar: _T.Union[str, _T.Tuple[str, ...]] = ...,
    dest: str = ...,
    version: str = ...,
    namespace_attrname=None,
    attrname_as_parsename=True,
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
    namespace_attrname=None,
    attrname_as_parsename=True,
    **kwargs: _T.Any
):
    all_kwds = {}
    if action != ...:
        all_kwds["action"] = action
    if nargs != ...:
        all_kwds["nargs"] = nargs
    if const != ...:
        all_kwds["const"] = const
    if default != ...:
        all_kwds["default"] = default
    if type != ...:
        all_kwds["type"] = type
    if choices != ...:
        all_kwds["choices"] = choices
    if required != ...:
        all_kwds["required"] = required
    if help != ...:
        all_kwds["help"] = help
    if metavar != ...:
        all_kwds["metavar"] = metavar
    if dest != ...:
        all_kwds["dest"] = dest
    if version != ...:
        all_kwds["version"] = version

    all_kwds = {**all_kwds, **kwargs}
    meta = {
        "is_key_args": attrname_as_parsename
    }

    return ParseArgsDescriptor(name=namespace_attrname, args=name_or_flags, kwds=all_kwds, meta=meta)
