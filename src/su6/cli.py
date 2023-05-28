"""This file contains all Typer Commands"""
import functools
from .core import DEFAULT_VERBOSITY, Verbosity, info, log_cmd_output, log_command, warn
import typing

import typer
from plumbum import local
from plumbum.commands.processes import CommandNotFound, ProcessExecutionError


from rich import print
GREEN_CIRCLE = "🟢"
YELLOW_CIRCLE = "🟡"
RED_CIRCLE = "🔴"

EXIT_CODE_SUCCESS = 0
EXIT_CODE_ERROR = 1
EXIT_CODE_COMMAND_NOT_FOUND = 127

app = typer.Typer()


def _check_tool(tool: str, *args: str, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Abstraction to run one of the cli checking tools and process its output

    Args:
        tool: the (bash) name of the tool to run
        verbosity: level of detail to print out (1 - 3). \
            Level 1 (quiet) will only print a colored circle indicating success/failure; \
            Level 2 (normal) will also print stdout/stderr; \
            Level 3 (verbose) will also print the executed command with its arguments.

    Todo:
        allow (optionally) specifying (default) target directory via cli or pyproject.toml,
        perhaps other settings too
    """
    try:
        cmd = local[tool]

        if verbosity >= 3:
            log_command(cmd, args)
        cmd(*args)
        print(GREEN_CIRCLE, tool)
        return EXIT_CODE_SUCCESS  # success
    except CommandNotFound:
        if verbosity > 2:
            warn(f"Tool {tool} not installed!")
        print(YELLOW_CIRCLE, tool)
        return EXIT_CODE_COMMAND_NOT_FOUND  # command not found
    except ProcessExecutionError as e:
        print(RED_CIRCLE, tool)
        if verbosity > 1:
            log_cmd_output(e.stdout, e.stderr)
        return EXIT_CODE_ERROR  # general error


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


@app.command()
@with_exit_code()
def ruff(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the Ruff Linter.

    Args:
        verbosity: level of detail to print out (1 - 3)
    """
    return _check_tool("ruff", ".", verbosity=verbosity)


@app.command()
@with_exit_code()
def black(
    fix: bool = False,

          verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the Black code formatter.

    Args:
        fix: if --fix is passed, black will be used to reformat the file(s).
        verbosity: level of detail to print out (1 - 3)
    """
    args = [".", "--exclude=venv.+|.+\.bak"]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check")

    return _check_tool("black", *args, verbosity=verbosity)


@app.command()
@with_exit_code()
def isort(fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the import sort (isort) utility.

    Args:
        fix: if --fix is passed, isort will be used to rearrange imports.
        verbosity: level of detail to print out (1 - 3)
    """
    args = ["."]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check-only")

    return _check_tool("isort", *args, verbosity=verbosity)


@app.command()
@with_exit_code()
def mypy(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the mypy static type checker.

    Args:
        verbosity: level of detail to print out (1 - 3)
    """
    return _check_tool("mypy", ".", verbosity=verbosity)


@app.command()
@with_exit_code()
def bandit(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the bandit security checker.

    Args:
        verbosity: level of detail to print out (1 - 3)
    """
    return _check_tool("bandit", "-r", "-c", "pyproject.toml", ".", verbosity=verbosity)


@app.command()
@with_exit_code()
def pydocstyle(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the pydocstyle docstring checker.

    Args:
        verbosity: level of detail to print out (1 - 3)
    """
    return _check_tool("pydocstyle", ".", verbosity=verbosity)


@app.command(name="all")
@with_exit_code()
def check_all(ignore_uninstalled: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY):
    """
    Run all available checks

    Args:
        ignore_uninstalled: use --ignore-uninstalled to skip exit code 127 (command not found)
        verbosity: level of detail to print out (1 - 3)
    """
    ignored_exit_codes = set()
    if ignore_uninstalled:
        ignored_exit_codes.add(EXIT_CODE_COMMAND_NOT_FOUND)

    return any(
        [
            ruff(verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes),
            black(verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes),
            mypy(verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes),
            bandit(verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes),
            isort(verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes),
            pydocstyle(verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes),
        ]
    )


@app.command(name="fix")
@with_exit_code()
def do_fix(verbosity: Verbosity = DEFAULT_VERBOSITY) -> bool:
    """
    Do everything that's safe to fix (so not ruff because that may break semantics).

    Args:
        verbosity: level of detail to print out (1 - 3)
    """
    return any(
        [
            black(fix=True, verbosity=verbosity, _suppress=True),
            isort(fix=True, verbosity=verbosity, _suppress=True),
        ]
    )


if __name__ == "__main__":
    app()
