"""
Provides a register decorator for third party plugins, and a `include_plugins` (used in cli.py) that loads them.
"""
import functools
import typing
from dataclasses import dataclass, field
from importlib.metadata import entry_points

from rich import print
from typer import Typer

from .core import (
    ApplicationState,
    T_Command,
    T_Command_Return,
    print_json,
    run_tool,
    state,
    with_exit_code,
)

__all__ = ["register", "run_tool", "PluginConfig", "print", "print_json"]


class PluginConfig:
    state: typing.Optional[ApplicationState]
    _extras: dict[str, typing.Any] | None = None
    _config_key = None

    def __init__(self, **kw: typing.Any) -> None:
        super().__init__()
        self.update(**kw)

    def __init_subclass__(cls, with_state: bool = False, config_key: str = None, **kwargs: typing.Any) -> None:
        super().__init_subclass__()
        cls._extras = {}  # own copy of extra's per subclass
        if with_state:
            cls._extras["state"] = state
            setattr(cls, "state", state)

        if config_key:
            cls._config_key = config_key

    def update(self, **kw: typing.Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)

    def _fields(self) -> typing.Generator[str, typing.Any, None]:
        yield from self.__annotations__.keys()
        if self._extras:
            yield from self._extras.keys()  # -> self.state in _values

    def _get(self, key: str) -> typing.Any:
        notfound = object()

        value = getattr(self, key, notfound)
        if value is not notfound:
            return value

        if self._extras:
            value = self._extras.get(key, notfound)
            if value is not notfound:
                return value

        msg = f"{key} not found in `self {self.__class__.__name__}`"
        if self._extras:
            msg += f" or `extra's {self._extras.keys()}`"
        raise KeyError(msg)

    def _values(self) -> typing.Generator[typing.Any, typing.Any, None]:
        yield from (self._get(k) for k in self._fields())

    def __repr__(self) -> str:
        # from dataclasses._repr_fn
        fields = self._fields()
        values = self._values()
        args = ", ".join([f"{f}={v!r}" for f, v in zip(fields, values)])
        name = self.__class__.__qualname__
        return f"{name}({args})"

    def __str__(self) -> str:
        return repr(self)


@dataclass
class PluginCommandRegistration:
    """
    When using the @register decorator, a Registration is created.

    `discover_plugins` will use this class to detect Registrations in a plugin module
    and `include_plugins` will add them to the top-level Typer app.
    """

    func: T_Command
    args: tuple[typing.Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, typing.Any] = field(default_factory=dict)

    @property
    def IS_SU6_REGISTRATION(self) -> bool:
        """
        Used to detect if a variable is a Registration.

        Even when isinstance() does not work because it's stored in memory in two different locations
        (-> e.g. in a plugin).

        See also, is_registration
        """
        return True

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> T_Command_Return:
        """
        You can still use a Plugin Registration as a normal function.
        """
        return self.func(*args, **kwargs)


T_Config = typing.Type[PluginConfig]
T_Wrappable = T_Config | T_Command
T_Register_Inner = PluginCommandRegistration | T_Config
T_Register_Outer = typing.Callable[[T_Wrappable], T_Register_Inner]


# T_Register_Outer = typing.Callable[[T_Wrappable], PluginCommandRegistration] | typing.Callable[[T_Wrappable], T_Config]
# T_Register_Outer_Command = typing.Callable[[T_Wrappable], PluginCommandRegistration]
# T_Register_Outer_Config = typing.Callable[[T_Wrappable], T_Config]


def _register_command(
    func_outer: T_Command,
    *a_outer: typing.Any,
    **kw_outer: typing.Any,
) -> PluginCommandRegistration:
    """
    Decorator used to add a top-level command to `su6`.

    Can either be used as @register() or @register.

    Args:
        func_outer: wrapped method
        a_outer: arguments passed to @register(arg1, arg2, ...) - should probably not be used!
        kw_outer: keyword arguments passed to @register(name=...) - will be passed to Typer's @app.command
    """
    return PluginCommandRegistration(func_outer, a_outer, kw_outer)


@typing.overload
def _register(wrappable: T_Config, *a: typing.Any, **kw: typing.Any) -> T_Config:
    ...


@typing.overload
def _register(wrappable: T_Command, *a: typing.Any, **kw: typing.Any) -> PluginCommandRegistration:
    ...


def _register(wrappable: T_Wrappable, *a: typing.Any, **kw: typing.Any) -> T_Register_Inner:
    if isinstance(wrappable, type) and issubclass(wrappable, PluginConfig):
        return _register_config(wrappable)
    elif callable(wrappable):
        # register as function
        return _register_command(wrappable, *a, **kw)
    else:
        raise NotImplementedError("...")


@typing.overload
def register(wrappable: T_Config, *a_outer: typing.Any, **kw_outer: typing.Any) -> T_Config:
    ...


@typing.overload
def register(wrappable: T_Command, *a_outer: typing.Any, **kw_outer: typing.Any) -> PluginCommandRegistration:
    ...


@typing.overload
def register(wrappable: None = None, *a_outer: typing.Any, **kw_outer: typing.Any) -> T_Register_Outer:
    ...


def register(
    wrappable: T_Wrappable = None, *a_outer: typing.Any, **kw_outer: typing.Any
) -> T_Register_Outer | T_Register_Inner:
    if wrappable:
        return _register(wrappable, *a_outer, **kw_outer)

    @typing.overload
    def inner(func: T_Command) -> PluginCommandRegistration:
        ...

    @typing.overload
    def inner(func: T_Config) -> T_Config:
        ...

    # else:
    def inner(func: T_Wrappable) -> T_Register_Inner:
        return _register(func, *a_outer, **kw_outer)

    return inner


def _register_config(_cls: T_Config) -> T_Config:
    return _cls


# list of registrations
T_Commands = list[PluginCommandRegistration]

# key: namespace
# value: app instance, docstring for 'help'
T_Namespaces = dict[str, tuple[Typer, str]]


def is_registration(something: typing.Any) -> bool:
    """
    Pytest might freak out if some package is pip installed and Registration exists locally.

    This method uses IS_SU6_REGISTRATION to check if the types actually match.
    """
    return getattr(something, "IS_SU6_REGISTRATION", False)


def discover_plugins() -> tuple[T_Namespaces, T_Commands]:
    """
    Using importlib.metadata, discover available su6 plugins.

    Example:
        # pyproject.toml
        # https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata
        [project.entry-points."su6"]
        demo = "su6_plugin_demo.cli"  # <- CHANGE ME
    """
    discovered_namespaces = {}
    discovered_commands = []
    discovered_plugins = entry_points(group="su6")
    for plugin in discovered_plugins:
        plugin_module = plugin.load()

        for item in dir(plugin_module):
            if item.startswith("_"):
                continue

            possible_command = getattr(plugin_module, item)

            if isinstance(possible_command, Typer):
                discovered_namespaces[plugin.name] = (possible_command, plugin_module.__doc__)
            elif is_registration(possible_command):
                discovered_commands.append(possible_command)

    return discovered_namespaces, discovered_commands


def include_plugins(app: Typer, _with_exit_code: bool = True) -> None:
    """
    Discover plugins using discover_plugins and add them to either global namespace or as a subcommand.

    Args:
        app: the top-level Typer app to append commands to
        _with_exit_code: should the @with_exit_code decorator be applied to the return value of the command?
    """
    namespaces, commands = discover_plugins()

    for namespace, (subapp, doc) in namespaces.items():
        # adding subcommand
        app.add_typer(subapp, name=namespace, help=doc)

    for registration in commands:
        if _with_exit_code:
            registration.func = with_exit_code()(registration.func)

        # adding top-level commands
        app.command(*registration.args, **registration.kwargs)(registration.func)


# todo:
# - add to 'all'
# - add to 'fix'
# - adding config keys

if typing.TYPE_CHECKING:
    # for mypy checking
    @register
    def without_braces() -> None:
        ...

    @register()
    def with_braces() -> None:
        ...

    @register(name="other")
    def with_kwargs() -> None:
        ...

    class NormalClass(PluginConfig):
        ...

    @register
    class ConfigWithoutBraces(PluginConfig):
        ...

    @register()
    class ConfigWithBraces(PluginConfig):
        ...

    cls1 = NormalClass
    inst1 = cls1()
    cls2 = ConfigWithoutBraces
    inst2 = cls2()
    # fixme:
    cls3 = ConfigWithBraces
    inst3 = cls3()
