"""This file contains all Typer Commands."""
import typing

import typer
from plumbum import local
from plumbum.commands.processes import CommandNotFound, ProcessExecutionError
from rich import print

from .core import (
    DEFAULT_VERBOSITY,
    EXIT_CODE_COMMAND_NOT_FOUND,
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    GREEN_CIRCLE,
    RED_CIRCLE,
    YELLOW_CIRCLE,
    Verbosity,
    get_su6_config,
    info,
    log_cmd_output,
    log_command,
    warn,
    with_exit_code,
)

app = typer.Typer()


def _check_tool(tool: str, *args: str, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Abstraction to run one of the cli checking tools and process its output.

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


# 'directory' is an optional cli argument to many commands, so we define the type here for reuse:
T_directory: typing.TypeAlias = typing.Annotated[str, typer.Argument()]  # = "."


@app.command()
@with_exit_code()
def ruff(directory: T_directory = None, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the Ruff Linter.

    Args:
        directory: where to run ruff on (default is current dir)
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)
    return _check_tool("ruff", config.directory, verbosity=verbosity)


@app.command()
@with_exit_code()
def black(directory: T_directory = None, fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the Black code formatter.

    Args:
        directory: where to run black on (default is current dir)
        fix: if --fix is passed, black will be used to reformat the file(s).
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)

    args = [config.directory, "--exclude=venv.+|.+\.bak"]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check")

    return _check_tool("black", *args, verbosity=verbosity)


@app.command()
@with_exit_code()
def isort(directory: T_directory = None, fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the import sort (isort) utility.

    Args:
        directory: where to run isort on (default is current dir)
        fix: if --fix is passed, isort will be used to rearrange imports.
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)
    args = [config.directory]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check-only")

    return _check_tool("isort", *args, verbosity=verbosity)


@app.command()
@with_exit_code()
def mypy(directory: T_directory = None, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the mypy static type checker.

    Args:
        directory: where to run mypy on (default is current dir)
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)
    return _check_tool("mypy", config.directory, verbosity=verbosity)


@app.command()
@with_exit_code()
def bandit(directory: T_directory = None, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the bandit security checker.

    Args:
        directory: where to run bandit on (default is current dir)
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)

    return _check_tool("bandit", "-r", "-c", config.pyproject, config.directory, verbosity=verbosity)


@app.command()
@with_exit_code()
def pydocstyle(directory: T_directory = None, verbosity: Verbosity = DEFAULT_VERBOSITY) -> int:
    """
    Runs the pydocstyle docstring checker.

    Args:
        directory: where to run pydocstyle on (default is current dir)
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)

    return _check_tool("pydocstyle", config.directory, verbosity=verbosity)


@app.command(name="all")
@with_exit_code()
def check_all(
    directory: T_directory = None, ignore_uninstalled: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY
) -> bool:
    """
    Run all available checks.

    Args:
        directory: where to run the tools on (default is current dir)
        ignore_uninstalled: use --ignore-uninstalled to skip exit code 127 (command not found)
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)

    ignored_exit_codes = set()
    if ignore_uninstalled:
        ignored_exit_codes.add(EXIT_CODE_COMMAND_NOT_FOUND)

    tools = config.determine_which_to_run([ruff, black, mypy, bandit, isort, pydocstyle])

    exit_codes = [tool(directory, verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes) for tool in tools]

    return any(exit_codes)


@app.command(name="fix")
@with_exit_code()
def do_fix(
    directory: T_directory = None, ignore_uninstalled: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY
) -> bool:
    """
    Do everything that's safe to fix (so not ruff because that may break semantics).

    Args:
        directory: where to run the tools on (default is current dir)
        ignore_uninstalled: use --ignore-uninstalled to skip exit code 127 (command not found)
        verbosity: level of detail to print out (1 - 3)
    """
    config = get_su6_config(directory=directory, verbosity=verbosity)

    ignored_exit_codes = set()
    if ignore_uninstalled:
        ignored_exit_codes.add(EXIT_CODE_COMMAND_NOT_FOUND)

    tools = config.determine_which_to_run([black, isort])

    exit_codes = [
        tool(directory, fix=True, verbosity=verbosity, _suppress=True, _ignore=ignored_exit_codes) for tool in tools
    ]

    return any(exit_codes)


# @app.callback()
# def main(config: str = None):
#     print(config)
#
#     # todo: allow user to specify su6 --config ./path/to/pyproject.toml <operation>


if __name__ == "__main__":
    app()
