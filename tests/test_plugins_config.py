from dataclasses import dataclass

import pytest
from configuraptor import Singleton
from configuraptor.errors import ConfigErrorExtraKey

from src.su6 import state
from src.su6.cli import app
from src.su6.plugins import PluginConfig, PluginLoader, register


class FakeModule1:
    @register(with_state=True)
    class MyPluginConfig(PluginConfig):
        ...

    @register(config_key="demo.extra")
    class NoState(PluginConfig):
        prop: str
        with_default: bool = True
        with_other_default: bool = True

    @register(config_key="demo2", strict=False)
    class Untyped(PluginConfig):
        empty: int


@dataclass
class FakeEntryPoint1:
    name: str

    def load(self):
        return FakeModule1()


def test_plugin_config():
    state_config = state.load_config(config_file="./pytest_examples/fake_module.toml")
    assert state_config.get_raw()

    fake_entry = FakeEntryPoint1(name="demo")
    assert PluginLoader(app, False)._load_plugin(fake_entry)

    inst1 = FakeModule1.MyPluginConfig()
    inst2 = FakeModule1.NoState()
    inst3 = FakeModule1.Untyped()

    assert inst1.state
    assert not getattr(inst2, "state", None)

    # assert state._plugins

    # normally done by `include_plugins` but our module is faked, so manual setup:
    state._setup_plugin_config_defaults()

    assert inst2.prop == "filled in"
    assert inst2.with_default == True
    assert inst2.with_other_default == False

    assert repr(inst2).startswith("FakeModule1.NoState(")
    assert "state=" in repr(inst1)
    assert "state=" not in repr(inst2)
    assert repr(inst1) == str(inst1)

    assert inst1._get("state")
    with pytest.raises(KeyError):
        inst1._get("non-existent")

    assert inst1._get("non-existent", strict=False) is None

    inst1.attach_extra("inst2", inst2)
    assert inst1._get("inst2") is inst2

    assert type(inst3.empty) != inst3.__annotations__["empty"]


def test_singleton():
    Singleton.clear()
    assert not Singleton._instances

    class MySingletonState(PluginConfig):
        ...

    inst1 = MySingletonState()
    inst2 = MySingletonState()
    assert inst1 is inst2

    with pytest.raises(ConfigErrorExtraKey):
        inst1.update(newkey="illegal")

    inst2.update(newkey="legal", _strict=False)
    inst2.update(newkey=None, _strict=False)

    assert inst1.newkey == "legal"  # and NOT None
    inst2.update(newkey=None, _strict=False, _allow_none=True)
    assert inst1.newkey is None

    assert inst1.__class__ in Singleton._instances
    Singleton.clear(inst1)
    assert inst2.__class__ not in Singleton._instances
