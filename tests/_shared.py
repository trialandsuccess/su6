import os
from pathlib import Path

tests_path = Path(os.path.dirname(os.path.realpath(__file__))).absolute().parent
EXAMPLES_PATH = tests_path / "pytest_examples"
GOOD_CODE = str(EXAMPLES_PATH / "good.py")
BAD_CODE = str(EXAMPLES_PATH / "bad.py")
