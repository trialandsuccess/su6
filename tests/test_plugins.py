import json

from su6_plugin_demo.cli import first, second, yet_another
from typer.testing import CliRunner

from src.su6.cli import app
from src.su6.plugins import registrations

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


# note: for some reason, the registration dict empties/changes in memory somewhere in testing so this does not work:

# def test_demo_properly_added_method1():
#     # method 1: top-level commands
#     result = runner.invoke(app, ["first"])
#     assert result.exit_code == 0
#
#     result = runner.invoke(app, ["second"])
#     assert result.exit_code == 1
#
#     result = runner.invoke(app, ["third"])
#     assert result.exit_code == 1
#
#     result = runner.invoke(app, ["fourth"])
#     assert result.exit_code > 0


def test_demo_properly_added_method2():
    # method 1: namespace commands
    result = runner.invoke(app, ["demo", "subcommand"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["demo", "nope"])
    assert result.exit_code > 0


def test_call_registration():
    assert not first()
    assert second()
    assert yet_another()
