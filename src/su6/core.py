"""
This file contains internal helpers used by cli.py.
"""
import enum
import functools
import inspect
import json
import operator
import pydoc
import sys
import types
import typing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, TypeAlias, Union

import configuraptor
import plumbum.commands.processes as pb
import tomli
import typer
from configuraptor import convert_config
from configuraptor.helpers import find_pyproject_toml
from plumbum import local
from plumbum.machines import LocalCommand
from rich import print

if typing.TYPE_CHECKING:  # pragma: no cover
    from .plugins import AnyRegistration

GREEN_CIRCLE = "🟢"
YELLOW_CIRCLE = "🟡"
RED_CIRCLE = "🔴"

EXIT_CODE_SUCCESS = 0
EXIT_CODE_ERROR = 1
EXIT_CODE_COMMAND_NOT_FOUND = 127


class ExitCodes:
    """
    Store the possible EXIT_CODE_ items for ease of use (and autocomplete).
    """

    # enum but not really
    success = EXIT_CODE_SUCCESS
    error = EXIT_CODE_ERROR
    command_not_found = EXIT_CODE_COMMAND_NOT_FOUND


PlumbumError = (pb.ProcessExecutionError, pb.ProcessTimedOut, pb.ProcessLineTimedOut, pb.CommandNotFound)

# a Command can return these:
T_Command_Return = bool | int | None
# ... here indicates any number of args/kwargs:
# t command is any @app.command() method, which can have anything as input and bool or int as output
T_Command: TypeAlias = Callable[..., T_Command_Return]
# t inner wrapper calls t_command and handles its output. This wrapper gets the same (kw)args as above so ... again
T_Inner_Wrapper: TypeAlias = Callable[..., int | None]
# outer wrapper gets the t_command method as input and outputs the inner wrapper,
# so that gets called() with args and kwargs when that method is used from the cli
T_Outer_Wrapper: TypeAlias = Callable[[T_Command], T_Inner_Wrapper]


def print_json(data: Any) -> None:
    """
    Take a dict of {command: output} or the State and print it.
    """
    indent = state.get_config().json_indent or None
    # none is different from 0 for the indent kwarg, but 0 will be changed to None for this module
    print(json.dumps(data, default=str, indent=indent))


def dump_tools_with_results(tools: list[T_Command], results: list[int | bool | None]) -> None:
    """
    When using format = json, dump the success of each tool in tools (-> exit code == 0).

    This method is used in `all` and `fix` (with a list of tools) and in 'with_exit_code' (with one tool).
    'with_exit_code' does NOT use this method if the return value was a bool, because that's the return value of
    'all' and 'fix' and those already dump a dict output themselves.

    Args:
        tools: list of commands that ran
        results: list of return values from these commands
    """
    print_json({tool.__name__: not result for tool, result in zip(tools, results)})


def with_exit_code() -> T_Outer_Wrapper:
    """
    Convert the return value of an app.command (bool or int) to an typer Exit with return code, \
    Unless the return value is Falsey, in which case the default exit happens (with exit code 0 indicating success).

    Usage:
    > @app.command()
    > @with_exit_code()
    def some_command(): ...

    When calling a command from a different command, _suppress=True can be added to not raise an Exit exception.
    """

    def outer_wrapper(func: T_Command) -> T_Inner_Wrapper:
        @functools.wraps(func)
        def inner_wrapper(*args: Any, **kwargs: Any) -> int:
            _suppress = kwargs.pop("_suppress", False)
            _ignore_exit_codes = kwargs.pop("_ignore", set())

            result = func(*args, **kwargs)
            if state.output_format == "json" and not _suppress and result is not None and not isinstance(result, bool):
                # isinstance(True, int) -> True so not isinstance(result, bool)
                # print {tool: success}
                # but only if a retcode is returned,
                # otherwise (True, False) assume the function handled printing itself.
                dump_tools_with_results([func], [result])

            if result is None:
                # assume no issue then
                result = 0

            if (retcode := int(result)) and not _suppress:
                raise typer.Exit(code=retcode)

            if retcode in _ignore_exit_codes:  # pragma: no cover
                # there is an error code, but we choose to ignore it -> return 0
                return ExitCodes.success

            return retcode

        return inner_wrapper

    return outer_wrapper


def is_available_via_python(tool: str) -> bool:
    """
    Sometimes, an executable is not available in PATH (e.g. via pipx) but it is available as `python -m something`.

    This tries to test for that.
        May not work for exceptions like 'semantic-release'/'semantic_release' (python-semantic-release)
    """
    try:
        pydoc.render_doc(tool)
        return True
    except ImportError:
        return False


def is_installed(tool: str, python_fallback: bool = True) -> bool:
    """
    Check whether a certain tool is installed (/ can be found via 'which').
    """
    try:
        return bool(local["which"](tool))
    except pb.ProcessExecutionError:
        return is_available_via_python(tool) if python_fallback else False


def on_tool_success(tool_name: str, result: str) -> int:
    """
    Last step of run_tool or run_tool_via_python on success.
    """
    if state.output_format == "text":
        print(GREEN_CIRCLE, tool_name)

    if state.verbosity > 2:  # pragma: no cover
        log_cmd_output(result)

    return ExitCodes.success  # success


def on_tool_missing(tool_name: str) -> int:
    """
    If tool can't be found in both run_tool and run_tool_via_python.
    """
    if state.verbosity > 2:
        warn(f"Tool {tool_name} not installed!")

    if state.output_format == "text":
        print(YELLOW_CIRCLE, tool_name)

    return ExitCodes.command_not_found  # command not found


def on_tool_failure(tool_name: str, e: pb.ProcessExecutionError) -> int:
    """
    If tool fails in run_tool or run_tool_via_python.
    """
    if state.output_format == "text":
        print(RED_CIRCLE, tool_name)

    if state.verbosity > 1:
        log_cmd_output(e.stdout, e.stderr)
    return ExitCodes.error  # general error


def run_tool_via_python(tool_name: str, *args: str) -> int:
    """
    Fallback: try `python -m tool ...` instead of `tool ...`.
    """
    cmd = local[sys.executable]["-m", tool_name]
    if state.verbosity >= 3:
        log_command(cmd, args)

    try:
        result = cmd(*args)
        return on_tool_success(tool_name, result)
    except pb.ProcessExecutionError as e:
        if "No module named" in e.stderr:
            return on_tool_missing(tool_name)

        return on_tool_failure(tool_name, e)


def run_tool(tool: str, *_args: str) -> int:
    """
    Abstraction to run one of the cli checking tools and process its output.

    Args:
        tool: the (bash) name of the tool to run.
        _args: cli args to pass to the cli bash tool
    """
    tool_name = tool.split("/")[-1]

    args = list(_args)

    if state.config and (extra_flags := state.config.get_default_flags(tool)):
        args.extend(extra_flags)

    try:
        cmd = local[tool]
    except pb.CommandNotFound:  # pragma: no cover
        return run_tool_via_python(tool_name, *args)

    if state.verbosity >= 3:
        log_command(cmd, args)

    try:
        result = cmd(*args)
        return on_tool_success(tool_name, result)

    except pb.ProcessExecutionError as e:
        return on_tool_failure(tool_name, e)


class Verbosity(enum.Enum):
    """
    Verbosity is used with the --verbose argument of the cli commands.
    """

    # typer enum can only be string
    quiet = "1"
    normal = "2"
    verbose = "3"
    debug = "4"  # only for internal use

    @staticmethod
    def _compare(
        self: "Verbosity",
        other: "Verbosity_Comparable",
        _operator: Callable[["Verbosity_Comparable", "Verbosity_Comparable"], bool],
    ) -> bool:
        """
        Abstraction using 'operator' to have shared functionality between <, <=, ==, >=, >.

        This enum can be compared with integers, strings and other Verbosity instances.

        Args:
            self: the first Verbosity
            other: the second Verbosity (or other thing to compare)
            _operator: a callable operator (from 'operators') that takes two of the same types as input.
        """
        match other:
            case Verbosity():
                return _operator(self.value, other.value)
            case int():
                return _operator(int(self.value), other)
            case str():
                return _operator(int(self.value), int(other))

    def __gt__(self, other: "Verbosity_Comparable") -> bool:
        """
        Magic method for self > other.
        """
        return self._compare(self, other, operator.gt)

    def __ge__(self, other: "Verbosity_Comparable") -> bool:
        """
        Method magic for self >= other.
        """
        return self._compare(self, other, operator.ge)

    def __lt__(self, other: "Verbosity_Comparable") -> bool:
        """
        Magic method for self < other.
        """
        return self._compare(self, other, operator.lt)

    def __le__(self, other: "Verbosity_Comparable") -> bool:
        """
        Magic method for self <= other.
        """
        return self._compare(self, other, operator.le)

    def __eq__(self, other: Union["Verbosity", str, int, object]) -> bool:
        """
        Magic method for self == other.

        'eq' is a special case because 'other' MUST be object according to mypy
        """
        if other is Ellipsis or other is inspect._empty:
            # both instances of object; can't use Ellipsis or type(ELlipsis) = ellipsis as a type hint in mypy
            # special cases where Typer instanciates its cli arguments,
            # return False or it will crash
            return False
        if not isinstance(other, (str, int, Verbosity)):
            raise TypeError(f"Object of type {type(other)} can not be compared with Verbosity")
        return self._compare(self, other, operator.eq)

    def __hash__(self) -> int:
        """
        Magic method for `hash(self)`, also required for Typer to work.
        """
        return hash(self.value)


Verbosity_Comparable = Verbosity | str | int

DEFAULT_VERBOSITY = Verbosity.normal


class Format(enum.Enum):
    """
    Options for su6 --format.
    """

    text = "text"
    json = "json"

    def __eq__(self, other: object) -> bool:
        """
        Magic method for self == other.

        'eq' is a special case because 'other' MUST be object according to mypy
        """
        if other is Ellipsis or other is inspect._empty:
            # both instances of object; can't use Ellipsis or type(ELlipsis) = ellipsis as a type hint in mypy
            # special cases where Typer instanciates its cli arguments,
            # return False or it will crash
            return False
        return self.value == other

    def __hash__(self) -> int:
        """
        Magic method for `hash(self)`, also required for Typer to work.
        """
        return hash(self.value)


DEFAULT_FORMAT = Format.text

C = typing.TypeVar("C", bound=T_Command)

DEFAULT_BADGE = "coverage.svg"


class AbstractConfig(configuraptor.TypedConfig, configuraptor.Singleton):
    """
    Used by state.config and plugin configs.
    """

    _strict = True


@dataclass
class Config(AbstractConfig):
    """
    Used as typed version of the [tool.su6] part of pyproject.toml.

    Also accessible via state.config
    """

    directory: str = "."
    pyproject: str = "pyproject.toml"
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    stop_after_first_failure: bool = False
    json_indent: int = 4
    docstyle_convention: Optional[str] = None
    default_flags: typing.Optional[dict[str, str | list[str]]] = field(default=None)

    ### pytest ###
    coverage: Optional[float] = None  # only relevant for pytest
    badge: bool | str = False  # only relevant for pytest

    def __post_init__(self) -> None:
        """
        Update the value of badge to the default path.
        """
        self.__raw: dict[str, Any] = {}
        if self.badge is True:  # pragma: no cover
            # no cover because pytest can't test pytest :C
            self.badge = DEFAULT_BADGE

    def determine_which_to_run(self, options: list[C], exclude: list[str] = None) -> list[C]:
        """
        Filter out any includes/excludes from pyproject.toml (first check include, then exclude).

        `exclude` via cli overwrites config option.
        """
        if self.include:
            tools = [_ for _ in options if _.__name__ in self.include and _.__name__ not in (exclude or [])]
            tools.sort(key=lambda f: self.include.index(f.__name__))
            return tools
        elif self.exclude or exclude:
            to_exclude = set((self.exclude or []) + (exclude or []))
            return [_ for _ in options if _.__name__ not in to_exclude]
        else:
            return options

    def determine_plugins_to_run(self, attr: str, exclude: list[str] = None) -> list[T_Command]:
        """
        Similar to `determine_which_to_run` but for plugin commands, and without 'include' ('exclude' only).

        Attr is the key in Registration to filter plugins on, e.g. 'add_to_all'
        """
        to_exclude = set((self.exclude or []) + (exclude or []))

        return [
            _.wrapped for name, _ in state._registered_plugins.items() if getattr(_, attr) and name not in to_exclude
        ]

    def set_raw(self, raw: dict[str, Any]) -> None:
        """
        Set the raw config dict (from pyproject.toml).

        Used to later look up Plugin config.
        """
        self.__raw.update(raw)

    def get_raw(self) -> dict[str, Any]:
        """
        Get the raw config dict (to load Plugin config).
        """
        return self.__raw or {}

    def get_default_flags(self, service: str) -> list[str]:
        """
        For a given service, load the additional flags from pyproject.toml.

        Example:
            [tool.su6.default-flags]
            mypy = "--disable-error-code misc"
            black = ["--include", "something", "--exclude", "something"]
        """
        if not self.default_flags:
            return []

        flags = self.default_flags.get(service, [])
        if not flags:
            return []

        if isinstance(flags, list):
            return flags
        elif isinstance(flags, str):
            return [_.strip() for _ in flags.split(" ") if _.strip()]
        raise TypeError(f"Invalid type {type(flags)} for flags.")


MaybeConfig: TypeAlias = Optional[Config]

T_typelike: TypeAlias = type | types.UnionType | types.UnionType


def _get_su6_config(overwrites: dict[str, Any], toml_path: Optional[str | Path] = None) -> MaybeConfig:
    """
    Parse the users pyproject.toml (found using black's logic) and extract the tool.su6 part.

    The types as entered in the toml are checked using _ensure_types,
    to make sure there isn't a string implicitly converted to a list of characters or something.

    Args:
        overwrites: cli arguments can overwrite the config toml.
        toml_path: by default, black will search for a relevant pyproject.toml.
                    If a toml_path is provided, that file will be used instead.
    """
    if toml_path is None:
        toml_path = find_pyproject_toml()

    if not toml_path:
        return None

    with open(toml_path, "rb") as f:
        full_config = tomli.load(f)

    tool_config = full_config["tool"]

    config = configuraptor.load_into(Config, tool_config, key="su6")

    config.update(pyproject=str(toml_path))
    config.update(**overwrites)
    # for plugins:
    config.set_raw(tool_config["su6"])

    return config


def get_su6_config(verbosity: Verbosity = DEFAULT_VERBOSITY, toml_path: str = None, **overwrites: Any) -> Config:
    """
    Load the relevant pyproject.toml config settings.

    Args:
        verbosity: if something goes wrong, level 3+ will show a warning and 4+ will raise the exception.
        toml_path: --config can be used to use a different file than ./pyproject.toml
        overwrites (dict[str, Any): cli arguments can overwrite the config toml.
                If a value is None, the key is not overwritten.
    """
    # strip out any 'overwrites' with None as value
    overwrites = convert_config(overwrites)

    try:
        if config := _get_su6_config(overwrites, toml_path=toml_path):
            return config
        raise ValueError("Falsey config?")
    except Exception as e:
        # something went wrong parsing config, use defaults
        if verbosity > 3:
            # verbosity = debug
            raise e
        elif verbosity > 2:
            # verbosity = verbose
            print("Error parsing pyproject.toml, falling back to defaults.", file=sys.stderr)
        return Config(**overwrites)


def info(*args: str) -> None:
    """
    'print' but with blue text.
    """
    print(f"[blue]{' '.join(args)}[/blue]", file=sys.stderr)


def warn(*args: str) -> None:
    """
    'print' but with yellow text.
    """
    print(f"[yellow]{' '.join(args)}[/yellow]", file=sys.stderr)


def danger(*args: str) -> None:
    """
    'print' but with red text.
    """
    print(f"[red]{' '.join(args)}[/red]", file=sys.stderr)


def log_command(command: LocalCommand, args: typing.Iterable[str]) -> None:
    """
    Print a Plumbum command in blue, prefixed with > to indicate it's a shell command.
    """
    info(f"> {command[args]}")


def log_cmd_output(stdout: str = "", stderr: str = "") -> None:
    """
    Print stdout in yellow and stderr in red.
    """
    # if you are logging stdout, it's probably because it's not a successful run.
    # However, it's not stderr so we make it warning-yellow
    warn(stdout)
    # probably more important error stuff, so stderr goes last:
    danger(stderr)


# postponed: use with Unpack later.
# class _Overwrites(typing.TypedDict, total=False):
#     config_file: Optional[str]
#     verbosity: Verbosity
#     output_format: Format
#     # + kwargs


@dataclass()
class ApplicationState:
    """
    Application State - global user defined variables.

    State contains generic variables passed BEFORE the subcommand (so --verbosity, --config, ...),
    whereas Config contains settings from the config toml file, updated with arguments AFTER the subcommand
    (e.g. su6 subcommand <directory> --flag), directory and flag will be updated in the config and not the state.

    To summarize: 'state' is applicable to all commands and config only to specific ones.
    """

    verbosity: Verbosity = DEFAULT_VERBOSITY
    output_format: Format = DEFAULT_FORMAT
    config_file: Optional[str] = None  # will be filled with black's search logic
    config: MaybeConfig = None

    def __post_init__(self) -> None:
        """
        Store registered plugin config.
        """
        self._plugin_configs: dict[str, AbstractConfig] = {}
        self._registered_plugins: dict[str, "AnyRegistration"] = {}

    def register_plugin(self, plugin_name: str, registration: "AnyRegistration") -> None:
        """
        Connect a Registration to the State.

        Used by `all` and `fix` to include plugin commands with add_to_all or add_to_fix respectively.
        """
        plugin_name = plugin_name.replace("_", "-")
        self._registered_plugins[plugin_name] = registration

    def load_config(self, **overwrites: Any) -> Config:
        """
        Load the su6 config from pyproject.toml (or other config_file) with optional overwriting settings.

        Also updates attached plugin configs.
        """
        if "verbosity" in overwrites:
            self.verbosity = overwrites["verbosity"]
        if "config_file" in overwrites:
            self.config_file = overwrites.pop("config_file")
        if "output_format" in overwrites:
            self.output_format = overwrites.pop("output_format")

        self.config = get_su6_config(toml_path=self.config_file, **overwrites)
        self._setup_plugin_config_defaults()
        return self.config

    def attach_plugin_config(self, name: str, config_cls: AbstractConfig) -> None:
        """
        Add a new plugin-specific config to be loaded later with load_config().

        Called from plugins.py when an @registered PluginConfig is found.
        """
        self._plugin_configs[name] = config_cls

    def _setup_plugin_config_defaults(self) -> None:
        """
        After load_config, the raw data is used to also fill registered plugin configs.
        """
        config = self.get_config()
        raw = config.get_raw()
        for name, config_instance in self._plugin_configs.items():
            configuraptor.load_into_instance(config_instance, raw, key=name, strict=config_instance._strict)

    def get_config(self) -> Config:
        """
        Get a filled config instance.
        """
        return self.config or self.load_config()

    def update_config(self, **values: Any) -> Config:
        """
        Overwrite default/toml settings with cli values.

        Example:
            `config = state.update_config(directory='src')`
            This will update the state's config and return the same object with the updated settings.
        """
        existing_config = self.get_config()

        values = convert_config(values)
        existing_config.update(**values)
        return existing_config


state = ApplicationState()
