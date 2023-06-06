import json
from dataclasses import dataclass

import pytest
from su6_plugin_demo.cli import first, second, yet_another
from typer.testing import CliRunner

from src.su6 import state
from src.su6.cli import app
from src.su6.core import Singleton, ApplicationState
from src.su6.plugins import PluginConfig, PluginLoader, register

runner = CliRunner(mix_stderr=False)


def test_demo_plugin_installed():  # pragma: nocover
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
# solution: faking it
#
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


class FakeModule2:
    # @register
    # class Config(PluginConfig):
    #     ...

    @register
    def func1():
        return None

    @register()
    def func2():
        return True

    @register(name="third")
    def func3(arg: str):
        return False


@dataclass
class FakeEntryPoint2:
    name: str

    def load(self):
        return FakeModule2()


def test_faked_commands_method1():
    state.load_config(config_file="./pytest_examples/fake_module.toml")
    fake_entry = FakeEntryPoint2(name="demo2")
    assert PluginLoader(app, True)._load_plugin(fake_entry)

    assert FakeModule2.func2() == True

    res = runner.invoke(app, ["func1"])
    assert res.exit_code == 0

    res = runner.invoke(app, ["func2"])
    assert res.exit_code == 1

    res = runner.invoke(app, ["func3"])
    assert res.exit_code > 0  # not found

    res = runner.invoke(app, ["third"])
    assert res.exit_code > 0  # incorrect signature

    res = runner.invoke(app, ["third", "arg"])
    assert res.exit_code == 0


def test_call_registration():
    assert not first()
    assert second()
    assert yet_another()
