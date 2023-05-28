"""
This file contains internal helpers used by cli.py.
"""
import enum
import inspect
import operator
import typing

from plumbum.machines import LocalCommand
from rich import print


class Verbosity(enum.Enum):
    """
    Verbosity is used with the --verbose argument of the cli commands.
    """

    # typer enum can only be string
    quiet = "1"
    normal = "2"
    verbose = "3"

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
