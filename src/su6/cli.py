import typer
from plumbum import local
from plumbum.commands.processes import ProcessExecutionError
from rich import print

from .core import DEFAULT_VERBOSITY, Verbosity, info, log_cmd_output, log_command

GREEN_CIRCLE = "🟢"
RED_CIRCLE = "🔴"

app = typer.Typer()


def _check_tool(tool: str, *args: str, verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    cmd = local[tool]

    try:
        if verbosity >= 3:
            log_command(cmd, args)
        cmd(*args)
        print(GREEN_CIRCLE, tool)
    except ProcessExecutionError as e:
        print(RED_CIRCLE, tool)
        if verbosity > 1:
            log_cmd_output(e.stdout, e.stderr)


@app.command()
def ruff(verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    return _check_tool("ruff", ".", verbosity=verbosity)


@app.command()
def black(fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    args = [".", "--exclude=venv.+|.+\.bak"]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check")

    return _check_tool("black", *args, verbosity=verbosity)


@app.command()
def isort(fix: bool = False, verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    args = ["."]
    if not fix:
        if verbosity > 3:
            info("note: running WITHOUT --check -> changing files")
        args.append("--check-only")

    return _check_tool("isort", *args, verbosity=verbosity)


@app.command()
def mypy(verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    return _check_tool("mypy", ".", verbosity=verbosity)


@app.command()
def bandit(verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    return _check_tool("bandit", "-r", "-c", "pyproject.toml", ".", verbosity=verbosity)


@app.command(name="all")
def check_all(verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    """
    Run all available checks
    """
    ruff(verbosity=verbosity)
    black(verbosity=verbosity)
    mypy(verbosity=verbosity)
    bandit(verbosity=verbosity)
    isort(verbosity=verbosity)


@app.command(name="fix")
def do_fix(verbosity: Verbosity = DEFAULT_VERBOSITY) -> None:
    """
    Do everything that's safe to fix (so not ruff because that may break semantics)
    """
    black(fix=True, verbosity=verbosity)
    isort(fix=True, verbosity=verbosity)


if __name__ == "__main__":
    app()
