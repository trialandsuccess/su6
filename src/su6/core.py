"""
This file contains internal helpers used by cli.py.
"""
import enum
import functools
import inspect
import json
import operator
import os
import sys
import tomllib
import types
import typing
from dataclasses import dataclass, field, replace

import black.files
import plumbum.commands.processes as pb
import typer
from plumbum.machines import LocalCommand
from rich import print
from typeguard import TypeCheckError
from typeguard import check_type as _check_type

GREEN_CIRCLE = "🟢"
YELLOW_CIRCLE = "🟡"
RED_CIRCLE = "🔴"

EXIT_CODE_SUCCESS = 0
EXIT_CODE_ERROR = 1
EXIT_CODE_COMMAND_NOT_FOUND = 127

PlumbumError = (pb.ProcessExecutionError, pb.ProcessTimedOut, pb.ProcessLineTimedOut, pb.CommandNotFound)

# ... here indicates any number of args/kwargs:
# t command is any @app.command() method, which can have anything as input and bool or int as output
T_Command: typing.TypeAlias = typing.Callable[..., bool | int]
# t inner wrapper calls t_command and handles its output. This wrapper gets the same (kw)args as above so ... again
T_Inner_Wrapper: typing.TypeAlias = typing.Callable[..., int]
# outer wrapper gets the t_command method as input and outputs the inner wrapper,
# so that gets called() with args and kwargs when that method is used from the cli
T_Outer_Wrapper: typing.TypeAlias = typing.Callable[[T_Command], T_Inner_Wrapper]


def print_json(data: dict[str, typing.Any]) -> None:
    """
    Take a dict of {command: output} or the State and print it.
    """
    print(json.dumps(data, default=str))


def dump_tools_with_results(tools: list[T_Command], results: list[int | bool]) -> None:
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
        def inner_wrapper(*args: typing.Any, **kwargs: typing.Any) -> int:
            _suppress = kwargs.pop("_suppress", False)
            _ignore_exit_codes = kwargs.pop("_ignore", set())

            result = func(*args, **kwargs)
            if state.output_format == "json" and not _suppress and not isinstance(result, bool):
                # isinstance(True, int) -> True so not isinstance(result, bool)
                # print {tool: success}
                # but only if a retcode is returned,
                # otherwise (True, False) assume the function handled printing itself.
                dump_tools_with_results([func], [result])

            if (retcode := int(result)) and not _suppress:
                raise typer.Exit(code=retcode)

            if retcode in _ignore_exit_codes:  # pragma: no cover
                # there is an error code, but we choose to ignore it -> return 0
                return EXIT_CODE_SUCCESS

            return retcode

        return inner_wrapper

    return outer_wrapper


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
        _operator: typing.Callable[["Verbosity_Comparable", "Verbosity_Comparable"], bool],
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

    def __eq__(self, other: typing.Union["Verbosity", str, int, object]) -> bool:
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


@dataclass
class Config:
    """
    Used as typed version of the [tool.su6] part of pyproject.toml.

    Also accessible via state.config
    """

    directory: str = "."
    pyproject: str = "pyproject.toml"
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    stop_after_first_failure: bool = False

    ### pytest ###
    coverage: typing.Optional[float] = None  # only relevant for pytest
    badge: bool | str = False  # only relevant for pytest

    def __post_init__(self) -> None:
        """
        Update the value of badge to the default path.
        """
        if self.badge is True:  # pragma: no cover
            # no cover because pytest can't test pytest :C
            self.badge = DEFAULT_BADGE

    def determine_which_to_run(self, options: list[C]) -> list[C]:
        """
        Filter out any includes/excludes from pyproject.toml (first check include, then exclude).
        """
        if self.include:
            tools = [_ for _ in options if _.__name__ in self.include]
            tools.sort(key=lambda f: self.include.index(f.__name__))
            return tools
        elif self.exclude:
            return [_ for _ in options if _.__name__ not in self.exclude]
        # if no include or excludes passed, just run all!
        return options


MaybeConfig: typing.TypeAlias = typing.Optional[Config]

T_typelike: typing.TypeAlias = type | types.UnionType | types.UnionType


def check_type(value: typing.Any, expected_type: T_typelike) -> bool:
    """
    Given a variable, check if it matches 'expected_type' (which can be a Union, parameterized generic etc.).

    Based on typeguard but this returns a boolean instead of returning the value or throwing a TypeCheckError
    """
    try:
        _check_type(value, expected_type)
        return True
    except TypeCheckError:
        return False


@dataclass
class ConfigError(Exception):
    """
    Raised if pyproject.toml [su6.tool] contains a variable of \
    which the type does not match that of the corresponding key in Config.
    """

    key: str
    value: typing.Any
    expected_type: type

    def __post_init__(self) -> None:
        """
        Store the actual type of the config variable.
        """
        self.actual_type = type(self.value)

    def __str__(self) -> str:
        """
        Custom error message based on dataclass values and calculated actual type.
        """
        return (
            f"Config key '{self.key}' had a value ('{self.value}') with a type (`{self.actual_type}`) "
            f"that was not expected: `{self.expected_type}` is the required type."
        )


T = typing.TypeVar("T")


def _ensure_types(data: dict[str, T], annotations: dict[str, type]) -> dict[str, T | None]:
    """
    Make sure all values in 'data' are in line with the ones stored in 'annotations'.

    If an annotated key in missing from data, it will be filled with None for convenience.
    """
    final: dict[str, T | None] = {}
    for key, _type in annotations.items():
        compare = data.get(key)
        if compare is None:
            # skip!
            continue
        if not check_type(compare, _type):
            raise ConfigError(key, value=compare, expected_type=_type)

        final[key] = compare
    return final


def _convert_config(items: dict[str, T]) -> dict[str, T]:
    """
    Converts the config dict (from toml) or 'overwrites' dict in two ways.

    1. removes any items where the value is None, since in that case the default should be used;
    2. replaces '-' in keys with '_' so it can be mapped to the Config properties.
    """
    return {k.replace("-", "_"): v for k, v in items.items() if v is not None}


def _get_su6_config(overwrites: dict[str, typing.Any], toml_path: str = None) -> MaybeConfig:
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
        toml_path = black.files.find_pyproject_toml((os.getcwd(),))

    if not toml_path:
        return None

    with open(toml_path, "rb") as f:
        full_config = tomllib.load(f)

    su6_config_dict = full_config["tool"]["su6"]
    su6_config_dict |= overwrites

    su6_config_dict["pyproject"] = toml_path
    # first convert the keys, then ensure types. Otherwise, non-matching keys may be removed!
    su6_config_dict = _convert_config(su6_config_dict)
    su6_config_dict = _ensure_types(su6_config_dict, Config.__annotations__)

    return Config(**su6_config_dict)


def get_su6_config(verbosity: Verbosity = DEFAULT_VERBOSITY, toml_path: str = None, **overwrites: typing.Any) -> Config:
    """
    Load the relevant pyproject.toml config settings.

    Args:
        verbosity: if something goes wrong, level 3+ will show a warning and 4+ will raise the exception.
        toml_path: --config can be used to use a different file than ./pyproject.toml
        overwrites (dict[str, typing.Any): cli arguments can overwrite the config toml.
                If a value is None, the key is not overwritten.
    """
    # strip out any 'overwrites' with None as value
    overwrites = _convert_config(overwrites)

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
    info(f"> {command[*args]}")


def log_cmd_output(stdout: str = "", stderr: str = "") -> None:
    """
    Print stdout in yellow and stderr in red.
    """
    # if you are logging stdout, it's probably because it's not a successful run.
    # However, it's not stderr so we make it warning-yellow
    warn(stdout)
    # probably more important error stuff, so stderr goes last:
    danger(stderr)


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
    config_file: typing.Optional[str] = None  # will be filled with black's search logic
    config: MaybeConfig = None

    def load_config(self, **overwrites: typing.Any) -> Config:
        """
        Load the su6 config from pyproject.toml (or other config_file) with optional overwriting settings.
        """
        if "verbosity" in overwrites:
            self.verbosity = overwrites["verbosity"]
        if "config_file" in overwrites:
            self.config_file = overwrites.pop("config_file")
        if "output_format" in overwrites:
            self.output_format = overwrites.pop("output_format")

        self.config = get_su6_config(toml_path=self.config_file, **overwrites)
        return self.config

    def update_config(self, **values: typing.Any) -> Config:
        """
        Overwrite default/toml settings with cli values.

        Example:
            `config = state.update_config(directory='src')`
            This will update the state's config and return the same object with the updated settings.
        """
        existing_config = self.load_config() if self.config is None else self.config

        values = _convert_config(values)
        # replace is dataclass' update function
        self.config = replace(existing_config, **values)
        return self.config


state = ApplicationState()
