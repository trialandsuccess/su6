import json
from dataclasses import dataclass

import typer
from typer.testing import CliRunner

from src.su6 import state
from src.su6.cli import app
from src.su6.plugins import PluginLoader, register
from su6.core import with_exit_code

runner = CliRunner(mix_stderr=False)


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


class FakeModule3:
    app = typer.Typer()

    @app.command()
    @with_exit_code()
    def subcommand() -> None:
        """
        Register a plugin-level command.

        Can be used as `su6 demo subcommand` (in this case, the plugin name is demo)
        """
        print("this lives in a namespace")

    @app.command()
    @with_exit_code()
    def exit_code() -> bool:
        """
        Register a plugin-level command.

        Can be used as `su6 demo subcommand` (in this case, the plugin name is demo)
        """
        print("this lives in a namespace")
        return True


@dataclass
class FakeEntryPoint3:
    name: str

    def load(self):
        return FakeModule3()


def test_sub_namespace():
    state.load_config(config_file="./pytest_examples/fake_module.toml")
    fake_entry = FakeEntryPoint3(name="demo3")
    assert PluginLoader(app, True)._load_plugin(fake_entry)

    res = runner.invoke(app, ["demo3", "subcommand"])
    assert res.exit_code == 0

    res = runner.invoke(app, ["demo3", "exit-code"])
    assert res.exit_code == 1
