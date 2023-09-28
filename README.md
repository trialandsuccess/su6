<div align="center">
    <img 
        align="center" 
        src="https://raw.githubusercontent.com/trialandsuccess/su6/master/_static/su6.png" 
        alt="su6 checker"
        width="400px"
        />
    <h1 align="center">su6</h1>
</div>

<div align="center">
    6 is pronounced as '/zɛs/' in Dutch, so 'su6' is basically 'success'. <br />
    This package will hopefully help achieve that!
</div>

<br>

<div align="center">
    <a href="https://pypi.org/project/su6"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/su6.svg"/></a>
    <a href="https://pypi.org/project/su6"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/su6.svg"/></a>
    <br/>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
    <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"/></a>
    <br/>
    <a href="https://github.com/trialandsuccess/su6/actions"><img alt="su6 checks" src="https://github.com/trialandsuccess/su6/actions/workflows/su6.yml/badge.svg?branch=development"/></a>
    <a href="https://github.com/trialandsuccess/su6/actions"><img alt="Coverage" src="coverage.svg"/></a>
</div>

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Plugins](#plugins)
- [License](#license)
- [Changelog](#changelog)

## Installation

```console
# quick install with all possible checkers:
pip install su6[all]
# or pick and choose checkers:
pip install [black,bandit,pydocstyle]
```

**Note**: this package does not work well with `pipx`, since a lot of the tools need to be in the same (virtual)
environment
of your code, in order to do proper analysis.

The following checkers are supported:

### ruff

- install: `pip install su6[ruff]`
- use: `su6 ruff [directory]`
- functionality: linter
- pypi: [ruff](https://pypi.org/project/ruff/)

### black

- install: `pip install su6[black]`
- use: `su6 black [directory] [--fix]`
- functionality: formatter
- pypi: [black](https://pypi.org/project/black/)

### mypy

- install: `pip install su6[mypy]`
- use: `su6 mypy [directory]`
- functionality: static type checker
- pypi: [mypy](https://pypi.org/project/mypy/)

### bandit

- install: `pip install su6[bandit]`
- use: `su6 bandit [directory]`
- functionality: security linter
- pypi: [bandit](https://pypi.org/project/bandit/)

### isort

- install: `pip install su6[isort]`
- use: `su6 isort [directory] [--fix]`
- functionality: import sorter
- pypi: [isort](https://pypi.org/project/isort/)

### pydocstyle

- install: `pip install su6[pydocstyle]`
- use: `su6 pydocstyle [directory]`
- functionality: docstring checker
- pypi: [pydocstyle](https://pypi.org/project/pydocstyle/)

### pytest

- install: `pip install su6[pytest]`
- use: `su6 pytest [directory] [--coverage <int>] [--json] [--html] [--badge <path>]`
- functionality: tester with coverage
- pypi: [pytest](https://pypi.org/project/pytest/), [pytest-cov](https://pypi.org/project/pytest-cov/)

## Usage

```console
su6 --help
# or, easiest to start:
su6 all
# usual signature:
su6 [--verbosity=1|2|3] [--config=...] [--format=text|json] <subcommand> [directory] [...specific options]
```

where `subcommand` is `all` or one of the available checkers;  
`verbosity` indicates how much information you want to see (default is '2').  
`config` allows you to select a different `.toml` file (default is `pyproject.toml`).  
`format` allows you to get a JSON output instead of the textual traffic lights (default is `text`).  
`directory` is the location you want to run the scans (default is current directory);  
In the case of `black` and `isort`, another optional parameter `--fix` can be passed.
This will allow the tools to do the suggested changes (if applicable).
Running `su6 fix` will run both these tools with the `--fix` flag.  
For `pytest`, `--json`, `--html`, `--badge <str>` and `--coverage <int>` are supported.
The latter two can also be configured in the pyproject.toml (see ['Configuration'](#configuration)).
The first two arguments can be used to control the output format of `pytest --cov`. Both options can be used at the same
time. The `--coverage` flag can be used to set a threshold for code coverage %. If the coverage is less than this
threshold, the check will fail.
If `badge` is set using cli or toml config, a SVG badge with the coverage % will be generated.
This badge can be used in for example the README.md.

### Configuration

In your `pyproject.toml`, you can add a `[tools.su6]` section to configure some of the behavior of this tools.
Currently, the following keys are supported:

```toml
[tool.su6]
directory = "." # string path to the directory on which to run all tools, e.g. 'src'
include = [] # list of checks to run (when calling `su6 all`), e.g. ['black', 'mypy']
exclude = [] # list of checks to skip (when calling `su6 all`), e.g. ['bandit']
stop-after-first-failure = false  # bool to indicate whether to exit 'all' after one failure or to do all checks
coverage = 100 # int threshold for pytest coverage 
badge = "coverage.svg"  # str path or bool (true | false) whether and where to output the coverage badge
```

All keys are optional. Note that if you have both an `include` as well as an `exclude`, all the tools in `include` will
run and `exclude` will be fully ignored.  
Additionally, the order in which the checks are defined in 'include', is the order in which they will run (in `all`
and `fix`)

### Github Action

In order to use this checker within Github to run checks after pushing,
you can add a workflow (e.g. `.github/workflows/su6.yaml`) like this example:

```yaml
name: run su6 checks
on:
  push:
    branches-ignore:
      - master
jobs:
  check:
    name: Check with `su6 all`
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip' # caching pip dependencies
      - run: pip install su6[all] .
      - run: su6 all
```

**Note:** if you don't want to run all checks, but specific ones only, you need to add the `--ignore-uninstalled` flag
to `su6 all`! Otherwise, Github will see exit code 127 (command missing) as a failure.

```yaml
name: run some su6 checks
on:
  push:
    branches-ignore:
      - master
jobs:
  check:
    name: Check with `su6 all`
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip' # caching pip dependencies
      - run: pip install su6[pycodestyle,black] .
      - run: su6 all --ignore-uninstalled  # ... other settings such as --stop-after-first-failure, --coverage ...
```

## Plugins

This tool also supports plugins to add extra checkers or other functionality.
See [docs/plugins.md](https://github.com/trialandsuccess/su6/blob/master/docs/plugins.md) for information on how to
build a Plugin.

### svelte-check

[robinvandernoord/su6-plugin-svelte-check](https://github.com/robinvandernoord/su6-plugin-svelte-check) is a Plugin that
adds `svelte-check` functionality.  
Can be installed using `pip install su6[svelte-check]`

### prettier

[robinvandernoord/su6-plugin-prettier](https://github.com/robinvandernoord/su6-plugin-prettier) is a Plugin that
adds `prettier.io` functionality.  
Can be installed using `pip install su6[prettier]`

## License

`su6` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

See `CHANGELOG.md` [on GitHub](https://github.com/trialandsuccess/su6/blob/master/CHANGELOG.md)
