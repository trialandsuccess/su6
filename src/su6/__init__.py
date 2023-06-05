"""
This file exposes 'app' to the module.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT

from .cli import app  # noqa: import is there for library reasons

# for plugins:
from .plugins import (  # noqa: import is there for library reasons
    register as register_plugin,
)
from .plugins import run_tool  # noqa: import is there for library reasons
