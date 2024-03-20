import json
import os
import shutil

import pytest
from typer.testing import CliRunner

from src.su6.__about__ import __version__
from src.su6.cli import app, run_tool
from src.su6.core import GREEN_CIRCLE, RED_CIRCLE, ExitCodes, PlumbumError

# by default, click's cli runner mixes stdout and stderr for some reason...
runner = CliRunner(mix_stderr=False)

from ._shared import BAD_CODE, EXAMPLES_PATH, GOOD_CODE


def test_ruff_good():
    result = runner.invoke(app, ["ruff", GOOD_CODE])
    assert result.exit_code == 0


def test_ruff_bad():
    result = runner.invoke(app, ["ruff", BAD_CODE])
    assert result.exit_code == 1


def test_black_good():
    result = runner.invoke(app, ["black", GOOD_CODE])
    assert result.exit_code == 0


def test_black_bad():
    result = runner.invoke(app, ["black", BAD_CODE])
    assert result.exit_code == 1


def test_black_fix():
    fixable_code = str(EXAMPLES_PATH / "fix_black.py")
    shutil.copyfile(BAD_CODE, fixable_code)
    try:
        # 1. assert error
        result = runner.invoke(app, ["black", fixable_code])
        assert result.exit_code == 1

        # 2. fix
        result = runner.invoke(app, ["--verbosity", "3", "black", fixable_code, "--fix"])
        assert result.exit_code == 0

        # 3. assert success
        result = runner.invoke(app, ["black", fixable_code])
        assert result.exit_code == 0
    finally:
        # cleanup
        os.unlink(fixable_code)


def test_mypy_good():
    result = runner.invoke(app, ["mypy", GOOD_CODE])
    assert result.exit_code == 0


def test_mypy_bad():
    result = runner.invoke(app, ["mypy", BAD_CODE])
    assert result.exit_code == 1


def test_bandit_good():
    result = runner.invoke(app, ["bandit", GOOD_CODE])
    assert result.exit_code == 0


def test_bandit_bad():
    result = runner.invoke(app, ["bandit", BAD_CODE])
    assert result.exit_code == 1


def test_isort_good():
    result = runner.invoke(app, ["isort", GOOD_CODE])
    assert result.exit_code == 0


def test_isort_bad():
    result = runner.invoke(app, ["isort", BAD_CODE])
    assert result.exit_code == 1


def test_isort_fix():
    fixable_code = str(EXAMPLES_PATH / "fix_isort.py")
    shutil.copyfile(BAD_CODE, fixable_code)
    try:
        # 1. assert error
        result = runner.invoke(app, ["isort", fixable_code])
        assert result.exit_code == 1

        # 2. fix
        result = runner.invoke(app, ["--verbosity", "3", "isort", fixable_code, "--fix"])
        assert result.exit_code == 0

        # 3. assert success
        result = runner.invoke(app, ["isort", fixable_code])
        assert result.exit_code == 0
    finally:
        # cleanup
        os.unlink(fixable_code)


def test_all_fix():
    fixable_code = str(EXAMPLES_PATH / "fix_all.py")
    shutil.copyfile(BAD_CODE, fixable_code)
    try:
        # 1. assert error
        result = runner.invoke(app, ["isort", fixable_code])
        assert result.exit_code == 1

        result = runner.invoke(app, ["black", fixable_code])
        assert result.exit_code == 1

        # 2. fix
        result = runner.invoke(
            app, ["--verbosity", "3", "--format", "json", "fix", fixable_code, "--ignore-uninstalled"]
        )
        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert data == {"black": True, "isort": True}

        # 3. assert success
        result = runner.invoke(app, ["isort", fixable_code])
        assert result.exit_code == 0

        result = runner.invoke(app, ["black", fixable_code])
        assert result.exit_code == 0
    finally:
        # cleanup
        os.unlink(fixable_code)


def test_pydocstyle_good():
    result = runner.invoke(app, ["pydocstyle", GOOD_CODE])
    assert result.exit_code == 0


def test_pydocstyle_bad():
    result = runner.invoke(app, ["pydocstyle", BAD_CODE])
    assert result.exit_code == 1


def test_all_good():
    args = ["--config", str(EXAMPLES_PATH / "except_pytest.toml"), "all", GOOD_CODE]
    # args = ["--config", str(EXAMPLES_PATH / "except_pytest.toml"), "--show-config"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    args = [
        "--config",
        str(EXAMPLES_PATH / "except_pytest.toml"),
        "--format",
        "json",
        "all",
        GOOD_CODE,
        "--ignore-uninstalled",
    ]

    result = runner.invoke(app, args)
    # can't really test without having everything installed,
    # but at least we can make sure the flag doen't crash anything!
    assert result.exit_code == 0

    results = json.loads(result.stdout)

    assert results == {
        "ruff": True,
        "black": True,
        "mypy": True,
        "bandit": True,
        "isort": True,
        "pydocstyle": True,
    }


def test_all_bad():
    args = ["--config", str(EXAMPLES_PATH / "except_pytest.toml"), "--format", "json", "all", BAD_CODE]
    result = runner.invoke(app, args)
    assert result.exit_code == 1

    results = json.loads(result.stdout)

    assert results == {
        "ruff": False,
        "black": False,
        "mypy": False,
        "bandit": False,
        "isort": False,
        "pydocstyle": False,
    }


### test_pytest is kind of an issue since this seems to hang the first running pytest session


def test_command_not_found():
    fake_tool = run_tool("xxx-should-never-exist-xxx")

    assert fake_tool == ExitCodes.command_not_found


def test_custom_include_exclude():
    code_file = str(EXAMPLES_PATH / "black_good_mypy_bad.py")

    result = runner.invoke(app, ["--config", str(EXAMPLES_PATH / "only_black.toml"), "all", code_file])
    assert result.exit_code == 0

    result = runner.invoke(app, ["--config", str(EXAMPLES_PATH / "only_mypy.toml"), "all", code_file])
    assert result.exit_code == 1


def test_json_format():
    code_file = str(EXAMPLES_PATH / "black_good_mypy_bad.py")
    args = [
        "--config",
        str(EXAMPLES_PATH / "only_black.toml"),
        "--verbosity",
        "3",
        "--format",
        "json",
        "all",
        code_file,
    ]
    result1 = runner.invoke(app, args)

    args = [
        "--config",
        str(EXAMPLES_PATH / "only_black.toml"),
        "--verbosity",
        "3",
        "--format",
        "json",
        "black",
        code_file,
    ]
    result2 = runner.invoke(app, args)

    data1 = json.loads(result1.stdout.strip())
    data2 = json.loads(result2.stdout.strip())
    assert data1 == data2 == {"black": True}

    args = [
        "--config",
        str(EXAMPLES_PATH / "only_mypy.toml"),
        "--verbosity",
        "3",
        "--format",
        "json",
        "all",
        code_file,
    ]
    result = runner.invoke(app, args)

    data = json.loads(result.stdout.strip())
    assert data == {"mypy": False}


def test_self_update():
    args = ["--format", "text", "--verbosity", "3", "self-update"]
    result = runner.invoke(app, args)

    assert GREEN_CIRCLE in result.stdout.strip()

    args = ["--format", "json", "self-update"]
    result = runner.invoke(app, args)

    data = json.loads(result.stdout.strip())
    assert data == {"self_update": True}


def test_self_update_invalid_version():
    args = [
        "--format",
        "text",
        "self-update",
        "--version",
        "0.0.0",
    ]
    result = runner.invoke(app, args)

    assert RED_CIRCLE in result.stdout.strip()

    args = [
        "--format",
        "json",
        "--verbosity",
        "3",
        "self-update",
        "--version",
        "0.0.0",
    ]
    result = runner.invoke(app, args)

    data = json.loads(result.stdout.strip())
    assert data == {"self_update": False}

    with pytest.raises(PlumbumError):
        args = [
            "--verbosity",
            "4",
            "self-update",
            "--version",
            "0.0.0",
        ]
        result = runner.invoke(app, args)
        raise result.exception


def test_missing_subcommand():
    result = runner.invoke(app, [])
    assert "missing subcommand" in result.stderr.lower()


def test_version_flag():
    args = ["--format", "json", "--version"]
    result = runner.invoke(app, args)
    data = json.loads(result.stdout.strip())
    assert data == {"version": __version__}

    args = ["--format", "text", "--version"]
    result = runner.invoke(app, args)
    assert __version__ in result.stdout


def test_stop_after_first_failure():
    # with cli flag
    args = [
        "--config",
        str(EXAMPLES_PATH / "except_pytest.toml"),
        "--format",
        "json",
        "all",
        BAD_CODE,
        "--stop-after-first-failure",
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 1

    results = json.loads(result.stdout)

    assert results == {
        "ruff": False,
    }

    # with toml
    args = ["--config", str(EXAMPLES_PATH / "stop_after_first.toml"), "--format", "json", "all", BAD_CODE]
    result = runner.invoke(app, args)
    assert result.exit_code == 1
    results = json.loads(result.stdout)

    assert results == {
        "ruff": False,
    }


def test_show_config_callback():
    # text
    args = ["--show-config"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert "ApplicationState(" in result.stdout and "Config(" in result.stdout

    # json
    args = [
        "--show-config",
        "--format",
        "json",
        "--verbosity",
        "3",
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 0

    data = json.loads(result.stdout)
    assert "Verbosity.verbose" in data["verbosity"]


def test_list():
    args = ["--config", str(EXAMPLES_PATH / "except_pytest.toml"), "list"]
    result = runner.invoke(app, args)

    print(result.stdout)

    assert result.exit_code == 0

    assert GREEN_CIRCLE in result.stdout
    assert RED_CIRCLE in result.stdout

    args = ["--format", "json"] + args
    result = runner.invoke(app, args)

    results = json.loads(result.stdout)

    assert results["ruff"] is True
    assert results["pytest"] is False
