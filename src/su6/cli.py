import functools
import typing

import typer
from plumbum import local
from plumbum.commands.processes import ProcessExecutionError
from rich import print

from .core import DEFAULT_VERBOSITY, Verbosity, info, log_cmd_output, log_command

GREEN_CIRCLE = "🟢"
RED_CIRCLE = "🔴"

app = typer.Typer()


def _check_tool(tool: str, *args: str, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    cmd = local[tool]

    try:
        if verbosity >= 3:
            log_command(cmd, args)
        cmd(*args)
        print(GREEN_CIRCLE, tool)
        return 0
    except ProcessExecutionError as e:
        print(RED_CIRCLE, tool)
        if verbosity > 1:
            log_cmd_output(e.stdout, e.stderr)
        return 1


# ... here indicates any number of args/kwargs:
# t command is any @app.command() method, which can have anything as input and bool or int as output
T_Command: typing.TypeAlias = typing.Callable[..., bool | int]
# t inner wrapper calls t_command and handles its output. This wrapper gets the same (kw)args as above so ... again
T_Inner_Wrapper: typing.TypeAlias = typing.Callable[..., None]
# outer wrapper gets the t_command method as input and outputs the inner wrapper,
# so that gets called() with args and kwargs when that method is used from the cli
T_Outer_Wrapper: typing.TypeAlias = typing.Callable[[T_Command], T_Inner_Wrapper]


def with_exit_code() -> T_Outer_Wrapper:
    """
    Convert the return value of an app.command (bool or int) to an typer Exit with return code,
    Unless the return value is Falsey, in which case the default exit happens (with exit code 0 indicating success)

    Usage:
    > @app.command()
    > @with_exit_code()
    def some_command(): ...

    When calling a command from a different command, _suppress=True can be added to not raise an Exit exception
    """

    def outer_wrapper(func: T_Command) -> T_Inner_Wrapper:
        @functools.wraps(func)
        def inner_wrapper(*args: typing.Any, **kwargs: typing.Any) -> None:
            _suppress = kwargs.pop("_suppress", False)

            if retcode := func(*args, **kwargs) and not _suppress:
                raise typer.Exit(code=int(retcode))

        return inner_wrapper

    return outer_wrapper


@app.command()
@with_exit_code()
def ruff(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    return _check_tool("ruff", ".", verbosity=verbosity)


@app.command()
@with_exit_code()
def black(fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    args = [".", "--exclude=venv.+|.+\.bak"]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check")

    return _check_tool("black", *args, verbosity=verbosity)


@app.command()
@with_exit_code()
def isort(fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    args = ["."]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check-only")

    return _check_tool("isort", *args, verbosity=verbosity)


@app.command()
@with_exit_code()
def mypy(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    return _check_tool("mypy", ".", verbosity=verbosity)


@app.command()
@with_exit_code()
def bandit(verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    return _check_tool("bandit", "-r", "-c", "pyproject.toml", ".", verbosity=verbosity)


@app.command(name="all")
@with_exit_code()
def check_all(verbosity: Verbosity = DEFAULT_VERBOSITY) -> bool:
    """
    Run all available checks
    """
    # don't exit just yet, only exit after this command!
    return not all(
        [
            ruff(verbosity=verbosity, _suppress=True),
            black(verbosity=verbosity, _suppress=True),
            mypy(verbosity=verbosity, _suppress=True),
            bandit(verbosity=verbosity, _suppress=True),
            isort(verbosity=verbosity, _suppress=True),
        ]
    )


@app.command(name="fix")
@with_exit_code()
def do_fix(verbosity: Verbosity = DEFAULT_VERBOSITY) -> bool:
    """
    Do everything that's safe to fix (so not ruff because that may break semantics)
    """
    return not all(
        [
            black(fix=True, verbosity=verbosity, _suppress=True),
            isort(fix=True, verbosity=verbosity, _suppress=True),
        ]
    )


if __name__ == "__main__":
    app()
