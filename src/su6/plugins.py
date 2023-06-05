"""
Provides a register decorator for third party plugins, and a `include_plugins` (used in cli.py) that loads them.
"""
import typing
from dataclasses import dataclass, field
from importlib.metadata import entry_points

from typer import Typer

from .core import T_Command, T_Command_Return, with_exit_code


@dataclass
class PluginRegistration:
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


T_Inner = typing.Callable[[T_Command], PluginRegistration]


@typing.overload
def register(
    func_outer: None = None,
    *a_outer: typing.Any,
    **kw_outer: typing.Any,
) -> T_Inner:
    """
    If func outer is None, a callback will be created that will return a Registration later.

    Example:
        @register()
        def command
    """


@typing.overload
def register(
    func_outer: T_Command,
    *a_outer: typing.Any,
    **kw_outer: typing.Any,
) -> PluginRegistration:
    """
    If func outer is a command, a registration will be created.

    Example:
        @register
        def command
    """


def register(
    func_outer: T_Command | None = None,
    *a_outer: typing.Any,
    **kw_outer: typing.Any,
) -> PluginRegistration | T_Inner:
    """
    Decorator used to add a top-level command to `su6`.

    Can either be used as @register() or @register.

    Args:
        func_outer: wrapped method
        a_outer: arguments passed to @register(arg1, arg2, ...) - should probably not be used!
        kw_outer: keyword arguments passed to @register(name=...) - will be passed to Typer's @app.command
    """
    if func_outer:
        # @register
        # def func
        return PluginRegistration(func_outer, a_outer, kw_outer)

    # @functools.wraps(func_outer)
    def inner(func_inner: T_Command) -> PluginRegistration:
        # @register()
        # def func

        # combine args/kwargs from inner and outer, just to be sure they are passed.
        return PluginRegistration(func_inner, a_outer, kw_outer)

    return inner


# list of registrations
T_Commands = list[PluginRegistration]

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
