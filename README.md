# su6-checker

[![PyPI - Version](https://img.shields.io/pypi/v/su6.svg)](https://pypi.org/project/su6)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/su6.svg)](https://pypi.org/project/su6)

-----
su6 (6 is pronounced as '/zɛs/' in Dutch, so 'su6' is basically 'success')  
This package will hopefully help achieve that!

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Changelog](#changelog)

## Installation

```console
# quick install with all possible checkers:
pip install su6[all]
# or pick and choose checkers:
pip install [black,bandit,pydocstyle]
```

**Note**: this package does not work well with `pipx`, since a lot of the tools need to be in the same (virtual) environment
of your code, in order to do proper analysis.

The following checkers are supported:

### ruff

- install: `pip install su6[ruff]`
- use: `su6 ruff`
- functionality: linter
- pypi: [ruff](https://pypi.org/project/ruff/)

### black

- install: `pip install su6[black]`
- use: `su6 black`, `su6 black --fix`
- functionality: formatter
- pypi: [black](https://pypi.org/project/black/)

### mypy

- install: `pip install su6[mypy]`
- use: `su6 mypy`
- functionality: static type checker
- pypi: [mypy](https://pypi.org/project/mypy/)

### bandit

- install: `pip install su6[bandit]`
- use: `su6 bandit`
- functionality: security linter
- pypi: [bandit](https://pypi.org/project/bandit/)

### isort

- install: `pip install su6[isort]`
- use: `su6 isort`, `su6 isort --fix`
- functionality: import sorter
- pypi: [isort](https://pypi.org/project/isort/)

### pydocstyle

- install: `pip install su6[pydocstyle]`
- use: `su6 pydocstyle`
- functionality: docstring checker
- pypi: [pydocstyle](https://pypi.org/project/pydocstyle/)

## Usage

```console
su6 --help
# or, easiest to start:
su6 all
```

## License

`su6` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

See `CHANGELOG.md` [on GitHub](https://github.com/robinvandernoord/su6-checker/blob/master/CHANGELOG.md)
