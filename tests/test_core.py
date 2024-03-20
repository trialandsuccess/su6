import contextlib
import sys
from dataclasses import dataclass

import pytest
from configuraptor import Singleton
from configuraptor.errors import ConfigErrorInvalidType

from src.su6.core import (
    ApplicationState,
    Config,
    ExitCodes,
    Verbosity,
    _get_su6_config,
    get_su6_config,
    is_available_via_python,
    is_installed,
    on_tool_failure,
    on_tool_missing,
    on_tool_success,
    run_tool,
    state, run_tool_via_python,
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


def test_get_default_flags(capsys):
    empty = Config()
    empty.default_flags = {
        "first": "string of flags",
        "second": ["list", "of", "flags"],
        "third": "",
        "fourth": [],
        "fifth": None,
        "sixth": {"illegal": "type"},
    }

    assert empty.get_default_flags("first") == ["string", "of", "flags"]
    assert empty.get_default_flags("second") == ["list", "of", "flags"]
    assert empty.get_default_flags("third") == []
    assert empty.get_default_flags("fourth") == []
    assert empty.get_default_flags("fifth") == []
    with pytest.raises(TypeError):
        assert empty.get_default_flags("sixth")

    capsys.readouterr()

    state.verbosity = 4
    Singleton.clear(state.config)
    state.load_config()
    state.config.default_flags = {"echo": ["uno", "dos", "tres"]}

    assert run_tool("echo") == ExitCodes.success
    captured = capsys.readouterr()

    assert "uno dos tres" in captured.err

    assert run_tool_via_python("__hello__") == ExitCodes.success
    captured = capsys.readouterr()
    assert "Hello world!" in captured.err

    # can not be found:
    assert run_tool_via_python("fake-news-xyz") == ExitCodes.command_not_found

    # can be found but fails:
    assert run_tool_via_python("su6.cli", "fail") == ExitCodes.error

    Singleton.clear(state.config)


def test_is_installed():
    assert is_installed("su6")
    assert not is_installed("some-fake-package")


def test_loading_state_without_load_config():
    state = ApplicationState()
    # skip state.load_config
    assert state.update_config() == get_su6_config()
    Singleton.clear(state.config)


def test_is_available_via_python():
    assert not is_installed("__hello__", python_fallback=False)
    assert is_installed("__hello__", python_fallback=True)
    assert is_available_via_python("__hello__")


@dataclass
class DummyError:
    stdout: str = ""
    stderr: str = ""


def test_on_tool_callbacks():
    # only for coverage tbh
    state.verbosity = Verbosity.verbose
    state.output_format = "text"

    assert on_tool_success("-", "") == ExitCodes.success
    assert on_tool_missing("-") == ExitCodes.command_not_found
    assert on_tool_failure("-", DummyError()) == ExitCodes.error
