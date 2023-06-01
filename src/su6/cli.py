"""This file contains all Typer Commands."""
import contextlib
import math
import os
import sys
import typing
from dataclasses import asdict
from json import load as json_load

import typer
from plumbum import local
from plumbum.commands.processes import CommandNotFound, ProcessExecutionError
from rich import print

from .__about__ import __version__
from .core import (
    DEFAULT_BADGE,
    DEFAULT_FORMAT,
    DEFAULT_VERBOSITY,
    EXIT_CODE_COMMAND_NOT_FOUND,
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    GREEN_CIRCLE,
    RED_CIRCLE,
    YELLOW_CIRCLE,
    Format,
    PlumbumError,
    Verbosity,
    dump_tools_with_results,
    info,
    log_cmd_output,
    log_command,
    print_json,
    state,
    warn,
    with_exit_code,
)

app = typer.Typer()


def _check_tool(tool: str, *args: str) -> int:
    """
    Abstraction to run one of the cli checking tools and process its output.

    Args:
        tool: the (bash) name of the tool to run.
        args: cli args to pass to the cli bash tool
    """
    try:
        cmd = local[tool]

        if state.verbosity >= 3:
            log_command(cmd, args)

        result = cmd(*args)

        if state.output_format == "text":
            print(GREEN_CIRCLE, tool)

        if state.verbosity > 2:  # pragma: no cover
            log_cmd_output(result)

        return EXIT_CODE_SUCCESS  # success
    except CommandNotFound:  # pragma: no cover
        if state.verbosity > 2:
            warn(f"Tool {tool} not installed!")

        if state.output_format == "text":
            print(YELLOW_CIRCLE, tool)

        return EXIT_CODE_COMMAND_NOT_FOUND  # command not found
    except ProcessExecutionError as e:
        if state.output_format == "text":
            print(RED_CIRCLE, tool)

        if state.verbosity > 1:
            log_cmd_output(e.stdout, e.stderr)
        return EXIT_CODE_ERROR  # general error


# 'directory' is an optional cli argument to many commands, so we define the type here for reuse:
T_directory: typing.TypeAlias = typing.Annotated[str, typer.Argument()]  # = "."


@app.command()
@with_exit_code()
def ruff(directory: T_directory = None) -> int:
    """
    Runs the Ruff Linter.

    Args:
        directory: where to run ruff on (default is current dir)

    """
    config = state.update_config(directory=directory)
    return _check_tool("ruff", config.directory)


@app.command()
@with_exit_code()
def black(directory: T_directory = None, fix: bool = False) -> int:
    """
    Runs the Black code formatter.

    Args:
        directory: where to run black on (default is current dir)
        fix: if --fix is passed, black will be used to reformat the file(s).

    """
    config = state.update_config(directory=directory)

    args = [config.directory, r"--exclude=venv.+|.+\.bak"]
    if not fix:
        args.append("--check")
    elif state.verbosity > 2:
        info("note: running WITHOUT --check -> changing files")

    return _check_tool("black", *args)


@app.command()
@with_exit_code()
def isort(directory: T_directory = None, fix: bool = False) -> int:
    """
    Runs the import sort (isort) utility.

    Args:
        directory: where to run isort on (default is current dir)
        fix: if --fix is passed, isort will be used to rearrange imports.

    """
    config = state.update_config(directory=directory)
    args = [config.directory]
    if not fix:
        args.append("--check-only")
    elif state.verbosity > 2:
        info("note: running WITHOUT --check -> changing files")

    return _check_tool("isort", *args)


@app.command()
@with_exit_code()
def mypy(directory: T_directory = None) -> int:
    """
    Runs the mypy static type checker.

    Args:
        directory: where to run mypy on (default is current dir)

    """
    config = state.update_config(directory=directory)
    return _check_tool("mypy", config.directory)


@app.command()
@with_exit_code()
def bandit(directory: T_directory = None) -> int:
    """
    Runs the bandit security checker.

    Args:
        directory: where to run bandit on (default is current dir)

    """
    config = state.update_config(directory=directory)
    return _check_tool("bandit", "-r", "-c", config.pyproject, config.directory)


@app.command()
@with_exit_code()
def pydocstyle(directory: T_directory = None) -> int:
    """
    Runs the pydocstyle docstring checker.

    Args:
        directory: where to run pydocstyle on (default is current dir)

    """
    config = state.update_config(directory=directory)
    return _check_tool("pydocstyle", config.directory)


@app.command(name="all")
@with_exit_code()
def check_all(
    directory: T_directory = None,
    ignore_uninstalled: bool = False,
    stop_after_first_failure: bool = None,
    # pytest:
    coverage: float = None,
    badge: bool = None,
) -> bool:
    """
    Run all available checks.

    Args:
        directory: where to run the tools on (default is current dir)
        ignore_uninstalled: use --ignore-uninstalled to skip exit code 127 (command not found)
        stop_after_first_failure: by default, the tool continues to run each test.
                But if you only want to know if everything passes,
                you could set this flag (or in the config toml) to stop early.

        coverage: pass to pytest()
        badge: pass to pytest()

    `def all()` is not allowed since this overshadows a builtin
    """
    config = state.update_config(
        directory=directory,
        stop_after_first_failure=stop_after_first_failure,
        coverage=coverage,
        badge=badge,
    )

    ignored_exit_codes = set()
    if ignore_uninstalled:
        ignored_exit_codes.add(EXIT_CODE_COMMAND_NOT_FOUND)

    tools = config.determine_which_to_run([ruff, black, mypy, bandit, isort, pydocstyle, pytest])

    exit_codes = []
    for tool in tools:
        a = [directory]
        kw = dict(_suppress=True, _ignore=ignored_exit_codes)

        if tool is pytest:  # pragma: no cover
            kw["coverage"] = config.coverage
            kw["badge"] = config.badge

        result = tool(*a, **kw)
        exit_codes.append(result)
        if config.stop_after_first_failure and result != 0:
            break

    if state.output_format == "json":
        dump_tools_with_results(tools, exit_codes)

    return any(exit_codes)


@app.command()
@with_exit_code()
def pytest(
    directory: T_directory = None,
    html: bool = False,
    json: bool = False,
    coverage: int = None,
    badge: bool = None,
) -> int:  # pragma: no cover
    """
    Runs all pytests.

    Args:
        directory: where to run pytests on (default is current dir)
        html: generate HTML coverage output?
        json: generate JSON coverage output?
        coverage: threshold for coverage (in %)
        badge: generate coverage badge (svg)? If you want to change the name, do this in pyproject.toml

    Example:
        > su6 pytest --coverage 50
        if any checks fail: exit 1 and red circle
        if all checks pass but coverage is less than 50%: exit 1, green circle for pytest and red for coverage
        if all check pass and coverage is at least 50%: exit 0, green circle for pytest and green for coverage

        if --coverage is not passed, there will be no circle for coverage.
    """
    config = state.update_config(directory=directory, coverage=coverage, badge=badge)

    if config.badge and config.coverage is None:
        # not None but still check cov
        config.coverage = 0

    args = ["--cov", config.directory]

    if config.coverage is not None:
        # json output required!
        json = True

    if html:
        args.extend(["--cov-report", "html"])

    if json:
        args.extend(["--cov-report", "json"])

    exit_code = _check_tool("pytest", *args)

    if config.coverage is not None:
        with open("coverage.json") as f:
            data = json_load(f)
            percent_covered = math.floor(data["totals"]["percent_covered"])

        # if actual coverage is less than the the threshold, exit code should be success (0)
        exit_code = percent_covered < config.coverage
        circle = RED_CIRCLE if exit_code else GREEN_CIRCLE
        if state.output_format == "text":
            print(circle, "coverage")

        if config.badge:
            if not isinstance(config.badge, str):
                # it's still True for some reason?
                config.badge = DEFAULT_BADGE

            with contextlib.suppress(FileNotFoundError):
                os.remove(config.badge)

            result = local["coverage-badge"]("-o", config.badge)
            if state.verbosity > 2:
                info(result)

    return exit_code


@app.command(name="fix")
@with_exit_code()
def do_fix(directory: T_directory = None, ignore_uninstalled: bool = False) -> bool:
    """
    Do everything that's safe to fix (so not ruff because that may break semantics).

    Args:
        directory: where to run the tools on (default is current dir)
        ignore_uninstalled: use --ignore-uninstalled to skip exit code 127 (command not found)

    `def fix()` is not recommended because other commands have 'fix' as an argument so those names would collide.
    """
    config = state.update_config(directory=directory)

    ignored_exit_codes = set()
    if ignore_uninstalled:
        ignored_exit_codes.add(EXIT_CODE_COMMAND_NOT_FOUND)

    tools = config.determine_which_to_run([black, isort])

    exit_codes = [tool(directory, fix=True, _suppress=True, _ignore=ignored_exit_codes) for tool in tools]

    if state.output_format == "json":
        dump_tools_with_results(tools, exit_codes)

    return any(exit_codes)


@app.command()
@with_exit_code()
def self_update(version: str = None) -> int:
    """
    Update `su6` to the latest (stable) version.

    Args:
        version: (optional) specific version to update to
    """
    python = sys.executable
    pip = local[python]["-m", "pip"]

    try:
        pkg = "su6"
        if version:
            pkg = f"{pkg}=={version}"

        args = ["install", "--upgrade", pkg]
        if state.verbosity >= 3:
            log_command(pip, args)

        output = pip(*args)
        if state.verbosity > 2:
            info(output)
        match state.output_format:
            case "text":
                print(GREEN_CIRCLE, "self-update")
            #  case json handled automatically by with_exit_code
        return 0
    except PlumbumError as e:
        if state.verbosity > 3:
            raise e
        elif state.verbosity > 2:
            warn(str(e))
        match state.output_format:
            case "text":
                print(RED_CIRCLE, "self-update")
            # case json handled automatically by with_exit_code
        return 1


def version_callback() -> typing.Never:
    """
    --version requested!
    """
    match state.output_format:
        case "text":
            print(f"su6 Version: {__version__}")
        case "json":
            print_json({"version": __version__})
    raise typer.Exit(0)


def show_config_callback() -> typing.Never:
    """
    --show-config requested!
    """
    match state.output_format:
        case "text":
            print(state)
        case "json":
            print_json(asdict(state))
    raise typer.Exit(0)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: str = None,
    verbosity: Verbosity = DEFAULT_VERBOSITY,
    output_format: typing.Annotated[Format, typer.Option("--format")] = DEFAULT_FORMAT,
    # stops the program:
    show_config: bool = False,
    version: bool = False,
) -> None:
    """
    This callback will run before every command, setting the right global flags.

    Args:
        ctx: context to determine if a subcommand is passed, etc
        config: path to a different config toml file
        verbosity: level of detail to print out (1 - 3)
        output_format: output format

        show_config: display current configuration?
        version: display current version?

    """
    state.load_config(config_file=config, verbosity=verbosity, output_format=output_format)

    if show_config:
        show_config_callback()
    elif version:
        version_callback()
    elif not ctx.invoked_subcommand:
        warn("Missing subcommand. Try `su6 --help` for more info.")
    # else: just continue


if __name__ == "__main__":  # pragma: no cover
    app()
