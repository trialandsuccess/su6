"""
This file contains internal helpers used by cli.py.
"""
import enum
import functools
import inspect
import operator
import os
import sys
import tomllib
import typing
from dataclasses import dataclass

import black.files
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

# ... here indicates any number of args/kwargs:
# t command is any @app.command() method, which can have anything as input and bool or int as output
T_Command: typing.TypeAlias = typing.Callable[..., bool | int]
# t inner wrapper calls t_command and handles its output. This wrapper gets the same (kw)args as above so ... again
T_Inner_Wrapper: typing.TypeAlias = typing.Callable[..., int]
# outer wrapper gets the t_command method as input and outputs the inner wrapper,
# so that gets called() with args and kwargs when that method is used from the cli
T_Outer_Wrapper: typing.TypeAlias = typing.Callable[[T_Command], T_Inner_Wrapper]


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

            if (retcode := int(func(*args, **kwargs))) and not _suppress:
                raise typer.Exit(code=retcode)

            if retcode in _ignore_exit_codes:
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

C = typing.TypeVar("C", bound=T_Command)


@dataclass
class Config:
    """
    Used as typed version of the [tool.su6] part of pyproject.toml.
    """

    directory: str = "."
    pyproject: str = "pyproject.toml"
    include: typing.Optional[list[str]] = None
    exclude: typing.Optional[list[str]] = None

    def determine_which_to_run(self, options: list[C]) -> list[C]:
        """
        Filter out any includes/excludes from pyproject.toml (first check include, then exclude).
        """
        if self.include:
            return [_ for _ in options if _.__name__ in self.include]
        elif self.exclude:
            return [_ for _ in options if _.__name__ not in self.exclude]
        # if no include or excludes passed, just run all!
        return options


def check_type(value: typing.Any, expected_type: type) -> bool:
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
    final = {}
    for key, _type in annotations.items():
        compare = data.get(key)
        if not check_type(compare, _type):
            raise ConfigError(key, value=compare, expected_type=_type)

        final[key] = compare
    return final


def _get_su6_config(overwrites: dict[str, typing.Any]) -> typing.Optional[Config]:
    """
    Parse the users pyproject.toml (found using black's logic) and extract the tool.su6 part.

    The types as entered in the toml are checked using _ensure_types,
    to make sure there isn't a string implicitly converted to a list of characters or something.

    Args:
        overwrites: cli arguments can overwrite the config toml.
    """
    toml_path = black.files.find_pyproject_toml((os.getcwd(),))
    if not toml_path:
        return None

    with open(toml_path, "rb") as f:
        full_config = tomllib.load(f)

    su6_config_dict = full_config["tool"]["su6"]
    su6_config_dict |= overwrites

    su6_config_dict["pyproject"] = toml_path
    su6_config_dict = _ensure_types(su6_config_dict, Config.__annotations__)

    return Config(**su6_config_dict)


def get_su6_config(verbosity: Verbosity = DEFAULT_VERBOSITY, **overwrites: typing.Any) -> typing.Optional[Config]:
    """
    Load the relevant pyproject.toml config settings.

    Args:
        verbosity: if something goes wrong, level 3+ will show a warning and 4+ will raise the exception.
        overwrites (dict[str, typing.Any): cli arguments can overwrite the config toml.
                If a value is None, the key is not overwritten.
    """
    # strip out any 'overwrites' with None as value
    overwrites = {k: v for k, v in overwrites.items() if v is not None}

    try:
        if config := _get_su6_config(overwrites):
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
    print(f"[blue]{' '.join(args)}[/blue]")


def warn(*args: str) -> None:
    """
    'print' but with yellow text.
    """
    print(f"[yellow]{' '.join(args)}[/yellow]")


def danger(*args: str) -> None:
    """
    'print' but with red text.
    """
    print(f"[red]{' '.join(args)}[/red]")


def log_command(command: LocalCommand, args: typing.Iterable[str]) -> None:
    """
    Print a Plumbum command in blue, prefixed with > to indicate it's a shell command.
    """
    info(f"> {command[*args]}")


def log_cmd_output(stdout: str, stderr: str) -> None:
    """
    Print stdout in yellow and stderr in red.
    """
    # if you are logging stdout, it's probably because it's not a successful run.
    # However, it's not stderr so we make it warning-yellow
    warn(stdout)
    # probably more important error stuff, so stderr goes last:
    danger(stderr)
