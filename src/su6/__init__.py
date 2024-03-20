"""
This file exposes 'app' to the module.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT

from rich import print

from .cli import app
from .core import GREEN_CIRCLE, RED_CIRCLE, YELLOW_CIRCLE, ExitCodes, print_json, state

# for plugins:
from .plugins import register as register_plugin
from .plugins import run_tool

__all__ = [
    "app",
    "print",
    "GREEN_CIRCLE",
    "RED_CIRCLE",
    "YELLOW_CIRCLE",
    "ExitCodes",
    "print_json",
    "state",
    "register_plugin",
    "run_tool",
]
