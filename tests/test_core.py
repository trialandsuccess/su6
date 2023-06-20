import contextlib
import os

import pytest
from configuraptor.errors import ConfigErrorInvalidType

from src.su6.core import (
    ApplicationState,
    Config,
    Verbosity,
    _get_su6_config,
    get_su6_config,
)

from ._shared import EXAMPLES_PATH

try:
    chdir = contextlib.chdir
except AttributeError:
    from contextlib_chdir import chdir


def test_verbosity_compare():
    verbosity_1 = Verbosity.quiet
    verbosity_2 = Verbosity.normal
    verbosity_3 = Verbosity.verbose

    assert verbosity_3 > verbosity_2 > verbosity_1
    assert str(verbosity_3.value) > verbosity_2 > str(verbosity_1.value)
    assert int(verbosity_3.value) > verbosity_2 > int(verbosity_1.value)
    assert str(verbosity_3.value) > verbosity_2 > int(verbosity_1.value)
    assert int(verbosity_3.value) > verbosity_2 > str(verbosity_1.value)

    assert str(verbosity_3.value) >= verbosity_2 >= str(verbosity_1.value)
    assert int(verbosity_3.value) >= verbosity_2 >= int(verbosity_1.value)
    assert str(verbosity_3.value) >= verbosity_2 >= int(verbosity_1.value)
    assert int(verbosity_3.value) >= verbosity_2 >= str(verbosity_1.value)

    assert str(verbosity_1.value) < verbosity_2 < str(verbosity_3.value)
    assert int(verbosity_1.value) < verbosity_2 < int(verbosity_3.value)
    assert str(verbosity_1.value) < verbosity_2 < int(verbosity_3.value)
    assert int(verbosity_1.value) < verbosity_2 < str(verbosity_3.value)

    assert str(verbosity_1.value) <= verbosity_2 <= str(verbosity_3.value)
    assert int(verbosity_1.value) <= verbosity_2 <= int(verbosity_3.value)
    assert str(verbosity_1.value) <= verbosity_2 <= int(verbosity_3.value)
    assert int(verbosity_1.value) <= verbosity_2 <= str(verbosity_3.value)

    assert verbosity_3 == verbosity_3.value
    assert verbosity_3 == str(verbosity_3.value)
    assert verbosity_3 == int(verbosity_3.value)

    with pytest.raises(TypeError):
        assert verbosity_3 == []


def test_get_su6_config():
    # doesnt_exist - defaults
    defaults = get_su6_config(toml_path="./doesnt-exist.toml")
    empty = get_su6_config(toml_path=str(EXAMPLES_PATH / "empty.toml"))
    none = get_su6_config(toml_path=None)
    assert Config() == defaults
    assert defaults.directory == empty.directory
    assert none.pyproject is not None

    with chdir("/tmp"):
        # no pyproject.toml in sight -> internal su6 config should return None and external should return default
        assert _get_su6_config(overwrites={}) is None
        assert get_su6_config() == defaults

    # invalid toml should raise exception on debug verbosity but default on other verbosities

    with pytest.raises(ConfigErrorInvalidType):
        get_su6_config(verbosity=Verbosity.debug, toml_path=str(EXAMPLES_PATH / "invalid.toml"))

    assert get_su6_config(verbosity=Verbosity.verbose, toml_path=str(EXAMPLES_PATH / "invalid.toml")) == defaults


def test_loading_state_without_load_config():
    state = ApplicationState()
    # skip state.load_config
    assert state.update_config() == get_su6_config()
