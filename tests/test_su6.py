import contextlib
import os
from pathlib import Path

from su6.cli import black, ruff, mypy, bandit, isort, pydocstyle

tests_path = Path(os.path.dirname(os.path.realpath(__file__)))
EXAMPLES_PATH = tests_path / "examples"
GOOD_CODE = str((EXAMPLES_PATH / "good.py").absolute())
BAD_CODE = str((EXAMPLES_PATH / "bad.py").absolute())


def test_ruff_good():
    assert ruff(GOOD_CODE, _suppress=True) == 0


def test_ruff_bad():
    assert ruff(BAD_CODE, _suppress=True) == 1


def test_black_good():
    assert black(GOOD_CODE, _suppress=True) == 0


def test_black_bad():
    assert black(BAD_CODE, _suppress=True) == 1


# fixme: mypy is being weird with directories!

# def test_mypy_good():
#     with contextlib.chdir(EXAMPLES_PATH):
#         assert mypy(GOOD_CODE, _suppress=True) == 0


# def test_mypy_bad():
#     with EXAMPLES_PATH:
#         assert mypy(BAD_CODE, _suppress=True) == 1


def test_bandit_good():
    assert bandit(GOOD_CODE, _suppress=True) == 0


def test_bandit_bad():
    assert bandit(BAD_CODE, _suppress=True) == 1


def test_isort_good():
    assert isort(GOOD_CODE, _suppress=True) == 0


def test_isort_bad():
    assert isort(BAD_CODE, _suppress=True) == 1


def test_pydocstyle_good():
    assert pydocstyle(GOOD_CODE, _suppress=True) == 0


def test_pydocstyle_bad():
    assert pydocstyle(BAD_CODE, _suppress=True) == 1
