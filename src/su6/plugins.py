"""
Provides a register decorator for third party plugins, and a `include_plugins` (used in cli.py) that loads them.
"""
import typing
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points

from rich import print
from typer import Typer

from .core import (
    AbstractConfig,
    ApplicationState,
    T_Command,
    print_json,
    run_tool,
    state,
    with_exit_code,
)

__all__ = ["register", "run_tool", "PluginConfig", "print", "print_json"]


class PluginConfig(AbstractConfig):
    """
    Can be inherited in plugin to load in plugin-specific config.

    The config class is a Singleton, which means multiple instances can be created, but they always have the same state.

    Example:
        @register()
        class DemoConfig(PluginConfig):
            required_arg: str
            boolean_arg: bool
            # ...


        config = DemoConfig()

        @register()
        def with_arguments(required_arg: str, boolean_arg: bool = False) -> None:
            config.update(required_arg=required_arg, boolean_arg=boolean_arg)
            print(config)
    """

    extras: dict[str, typing.Any]
    state: typing.Optional[ApplicationState]  # only with @register(with_state=True) or after self.attach_state

    def __init__(self, **kw: typing.Any) -> None:
        """
        Initial variables can be passed on instance creation.
        """
        super().__init__()
        self.update(**kw)
        self.extras = {}

    def attach_extra(self, name: str, obj: typing.Any) -> None:
        """
        Add a non-annotated variable.
        """
        self.extras[name] = obj

    def attach_state(self, global_state: ApplicationState) -> None:
        """
        Connect the global state to the plugin config.
        """
        self.state = global_state
        self.attach_extra("state", global_state)

    def _fields(self) -> typing.Generator[str, typing.Any, None]:
        yield from self.__annotations__.keys()
        if self.extras:
            yield from self.extras.keys()  # -> self.state in _values

    def _get(self, key: str, strict: bool = True) -> typing.Any:
        notfound = object()

        value = getattr(self, key, notfound)
        if value is not notfound:
            return value

        if self.extras:
            value = self.extras.get(key, notfound)
            if value is not notfound:
                return value

        if strict:
            msg = f"{key} not found in `self {self.__class__.__name__}`"
            if self.extras:
                msg += f" or `extra's {self.extras.keys()}`"
            raise KeyError(msg)

    def _values(self) -> typing.Generator[typing.Any, typing.Any, None]:
        yield from (self._get(k, False) for k in self._fields())

    def __repr__(self) -> str:
        """
        Create a readable representation of this class with its data.

        Stolen from dataclasses._repr_fn.
        """
        fields = self._fields()
        values = self._values()
        args = ", ".join([f"{f}={v!r}" for f, v in zip(fields, values)])
        name = self.__class__.__qualname__
        return f"{name}({args})"

    def __str__(self) -> str:
        """
        Alias for repr.
        """
        return repr(self)


T_PluginConfig = typing.Type[PluginConfig]

U_Wrappable = typing.Union[T_PluginConfig, T_Command]
T_Wrappable = typing.TypeVar("T_Wrappable", T_PluginConfig, T_Command)


@dataclass()
class Registration(typing.Generic[T_Wrappable]):
    wrapped: T_Wrappable

    # Command:
    add_to_all: bool
    add_to_fix: bool

    # Config:
    with_state: bool
    strict: bool
    config_key: typing.Optional[str]

    args: tuple[typing.Any, ...]
    kwargs: dict[str, typing.Any]

    @property
    def what(self) -> typing.Literal["command", "config"] | None:
        if isinstance(self.wrapped, type) and issubclass(self.wrapped, PluginConfig):
            return "config"
        elif callable(self.wrapped):
            return "command"


AnyRegistration = Registration[T_PluginConfig] | Registration[T_Command]

# WeakValueDictionary() does not work since it removes the references too soon :(
registrations: dict[int, AnyRegistration] = {}


def _register(
    wrapped: T_Wrappable,
    add_to_all: bool,
    add_to_fix: bool,
    with_state: bool,
    strict: bool,
    config_key: typing.Optional[str],
    *a: typing.Any,
    **kw: typing.Any,
) -> T_Wrappable:
    registration = Registration(
        wrapped,
        # Command:
        add_to_all=add_to_all,
        add_to_fix=add_to_fix,
        # Config:
        with_state=with_state,
        strict=strict,
        config_key=config_key,
        # passed to Typer
        args=a,
        kwargs=kw,
    )

    registrations[id(wrapped)] = registration
    state.register_plugin(wrapped.__name__, registration)

    return wrapped


@typing.overload
def register(wrappable: T_Wrappable, *a_outer: typing.Any, **kw_outer: typing.Any) -> T_Wrappable:
    """
    If wrappable is passed, it returns the same type.

    @register
    def func(): ...

    -> register(func) is called
    """


@typing.overload
def register(
    wrappable: None = None, *a_outer: typing.Any, **kw_outer: typing.Any
) -> typing.Callable[[T_Wrappable], T_Wrappable]:
    """
    If wrappable is None (empty), it returns a callback that will wrap the function later.

    @register()
    def func(): ...

    -> register() is called
    """


def register(
    wrappable: T_Wrappable = None,
    # only used when @registering a Command:
    add_to_all: bool = False,
    add_to_fix: bool = False,
    # only used when @registering a PluginConfig:
    with_state: bool = False,
    strict: bool = True,
    config_key: typing.Optional[str] = None,
    *a_outer: typing.Any,
    **kw_outer: typing.Any,
) -> T_Wrappable | typing.Callable[[T_Wrappable], T_Wrappable]:
    """
    Register a top-level Plugin command or a Plugin Config.

    Examples:
        @register() # () are optional, but you can add Typer keyword arguments if needed.
        def command():
            # 'su6 command' is now registered!
            ...

        @register() # () are optional, but extra keyword arguments can be passed to configure the config.
        class MyConfig(PluginConfig):
            property: str
    """

    def inner(func: T_Wrappable) -> T_Wrappable:
        return _register(func, add_to_all, add_to_fix, with_state, strict, config_key, *a_outer, **kw_outer)

    if wrappable:
        return inner(wrappable)
    else:
        return inner


T = typing.TypeVar("T")


class BoundMethodOf(typing.Protocol[T]):
    """
    Protocol to define properties that a bound method has.
    """

    __self__: T
    __name__: str  # noqa: A003 - property does exist on the class
    __doc__: typing.Optional[str]  # noqa: A003 - property does exist on the class

    def __call__(self, a: int) -> str:  # pragma: no cover
        """
        Indicates this Protocol type can be called.
        """


Unbound = typing.Callable[..., typing.Any]


def unbind(meth: BoundMethodOf[typing.Any] | Unbound) -> typing.Optional[Unbound]:
    """
    Extract the original function (which has a different id) from a class method.
    """
    return getattr(meth, "__func__", None)


@dataclass()
class PluginLoader:
    app: Typer
    with_exit_code: bool

    def main(self) -> None:
        """
        Using importlib.metadata, discover available su6 plugins.

        Example:
            # pyproject.toml
            # https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata
            [project.entry-points."su6"]
            demo = "su6_plugin_demo.cli"  # <- CHANGE ME
        """
        discovered_plugins = entry_points(group="su6")
        for plugin in discovered_plugins:  # pragma: nocover
            self._load_plugin(plugin)

        self._cleanup()

    def _cleanup(self) -> None:
        # registrations.clear()
        ...

    def _load_plugin(self, plugin: EntryPoint) -> list[str]:
        """
        Look for typer instances and registered commands and configs in an Entrypoint.

        [project.entry-points."su6"]
        demo = "su6_plugin_demo.cli"

        In this case, the entrypoint 'demo' is defined and points to the cli.py module,
        which gets loaded with `plugin.load()` below.
        """
        result = []
        plugin_module = plugin.load()

        for item in dir(plugin_module):
            if item.startswith("_"):
                continue

            possible_command = getattr(plugin_module, item)

            # get method by id (in memory) or first unbind from class and then get by id
            registration = registrations.get(id(possible_command)) or registrations.get(id(unbind(possible_command)))

            if isinstance(possible_command, Typer):
                result += self._add_subcommand(plugin.name, possible_command, plugin_module.__doc__)
            elif registration and registration.what == "command":
                result += self._add_command(plugin.name, typing.cast(Registration[T_Command], registration))
            elif registration and registration.what == "config":
                result += self._add_config(plugin.name, typing.cast(Registration[T_PluginConfig], registration))
                # else: ignore

        return result

    def _add_command(self, _: str, registration: Registration[T_Command]) -> list[str]:
        """
        When a Command Registration is found, it is added to the top-level namespace.
        """
        if self.with_exit_code:
            registration.wrapped = with_exit_code()(registration.wrapped)
        # adding top-level commands
        self.app.command(*registration.args, **registration.kwargs)(registration.wrapped)
        return [f"command {_}"]

    def _add_config(self, name: str, registration: Registration[T_PluginConfig]) -> list[str]:
        """
        When a Config Registration is found, the Singleton data is updated with config from pyproject.toml.

        Example:
            # pyproject.toml
            [tool.su6.demo]
            boolean-arg = true
            optional-with-default = "overridden"

            [tool.su6.demo.extra]
            more = true
        """
        key = registration.config_key or name

        cls = registration.wrapped
        inst = cls()

        if registration.with_state:
            inst.attach_state(state)

        if registration.strict is False:
            inst._strict = False

        state.attach_plugin_config(key, inst)
        return [f"config {name}"]

    def _add_subcommand(self, name: str, subapp: Typer, doc: str) -> list[str]:
        self.app.add_typer(subapp, name=name, help=doc)
        return [f"subcommand {name}"]


def include_plugins(app: Typer, _with_exit_code: bool = True) -> None:
    """
    Discover plugins using discover_plugins and add them to either global namespace or as a subcommand.

    Args:
        app: the top-level Typer app to append commands to
        state: top-level application state
        _with_exit_code: should the @with_exit_code decorator be applied to the return value of the command?
    """
    loader = PluginLoader(app, _with_exit_code)
    loader.main()


# todo:
# - add to 'all'
# - add to 'fix'
