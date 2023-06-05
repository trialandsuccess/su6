import json

from su6_plugin_demo.cli import first, second, yet_another
from typer.testing import CliRunner

from src.su6.cli import app
from src.su6.plugins import discover_plugins

runner = CliRunner(mix_stderr=False)


def _ensure_demo_plugin_installed():  # pragma: nocover
    result = runner.invoke(app, ["plugins"])
    assert result.exit_code == 0

    assert "installed plugins" in result.stdout.lower()

    result = runner.invoke(app, ["--format", "json", "plugins"])
    assert result.exit_code == 0

    data = json.loads(result.stdout)

    # should be at least one plugin
    assert data

    if "demo" not in data:
        raise EnvironmentError("su6-plugin-demo is not installed! Can't test this package properly.")


def test_discover_plugins():
    _ensure_demo_plugin_installed()
    namespaces, commands = discover_plugins()

    print(namespaces, commands)
    assert namespaces
    assert commands


def test_demo_properly_added_method1():
    # method 1: top-level commands
    result = runner.invoke(app, ["first"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["second"])
    assert result.exit_code == 1

    result = runner.invoke(app, ["third"])
    assert result.exit_code == 1

    result = runner.invoke(app, ["fourth"])
    assert result.exit_code > 0


def test_demo_properly_added_method2():
    # method 1: namespace commands
    result = runner.invoke(app, ["demo", "subcommand"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["demo", "nope"])
    assert result.exit_code > 0


def test_call_registration():
    assert not first()
    assert second(_suppress=True)
    assert yet_another(_suppress=True)
