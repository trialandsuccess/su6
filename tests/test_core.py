import contextlib

import pytest

from src.su6.core import (
    ApplicationState,
    Config,
    ConfigError,
    Verbosity,
    _ensure_types,
    _get_su6_config,
    check_type,
    get_su6_config,
)

from ._shared import EXAMPLES_PATH


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


def test_check_type():
    assert check_type("str", str | int)
    assert check_type([1, 2, 3], list[int])
    assert check_type([1, 2, 3], list[int] | int)
    assert not check_type([1, 2, 3], list[str])


def test_ensure_types():
    assert _ensure_types({"float": 3.5}, {"float": float})
    with pytest.raises(ConfigError):
        try:
            _ensure_types({"float": "not-a-float"}, {"float": float})
        except ConfigError as e:
            assert "float" in str(e) and "str" in str(e)
            raise e


def test_get_su6_config():
    # doesnt_exist - defaults
    defaults = get_su6_config(toml_path="./doesnt-exist.toml")
    empty = get_su6_config(toml_path=str(EXAMPLES_PATH / "empty.toml"))
    none = get_su6_config(toml_path=None)
    assert Config() == defaults
    assert defaults.directory == empty.directory
    assert none.pyproject is not None

    with contextlib.chdir("/tmp"):
        # no pyproject.toml in sight -> internal su6 config should return None and external should return default
        assert _get_su6_config(overwrites={}) is None
        assert get_su6_config() == defaults

    # invalid toml should raise exception on debug verbosity but default on other verbosities

    with pytest.raises(ConfigError):
        get_su6_config(verbosity=Verbosity.debug, toml_path=str(EXAMPLES_PATH / "invalid.toml"))

    assert get_su6_config(verbosity=Verbosity.verbose, toml_path=str(EXAMPLES_PATH / "invalid.toml")) == defaults


def test_loading_state_without_load_config():
    state = ApplicationState()
    # skip state.load_config
    assert state.update_config() == get_su6_config()
