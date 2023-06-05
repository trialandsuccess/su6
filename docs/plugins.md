# Plugins

To add more checkers or other functionality, `su6` can be extended with plugins.  
You can use [this template repository] to get some boilerplate code.

## pyproject.toml

```toml
# in your plugin's pyproject.toml:
dependencies = [
    "su6"
]

# https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata
[project.entry-points."su6"]
demo = "su6_plugin_demo.cli"  # <- CHANGE ME
```

This registers your plugin's `cli.py` in the namespace `demo` to the `su6` package.

## Example Code

```python
# cli.py

from su6.plugins import register


# or: from su6 import register_plugin


# method 1: adding top-level commands

@register
def first():
    print("This is a demo  command!")


@register()  # register with or without braces is possible
def second():
    print("This is a demo  command!")


@register(name="third")  # keyword arguments will be forwarded to Typer's @app.command
def other():
    print("This is a demo  command!")


# method 2: adding a namespace (based on the plugin package name)

from typer import Typer

app = Typer()


@app.command()
def subcommand():
    print("this lives in a namespace")

```

In this case, the following commands would be available in the `su6` tool after installing this plugin:

```bash
# method 1:
su6 first
su6 second
su6 third
# method 2:
su6 demo subcommand
```

## Creating Checks

`su6` also exposes the `run_tool` function. This function runs a bash command (with arguments) and checks the status
code. It will automatically generate the right output based on the user's `--format`, so a stoplight by default
or `json` output if requested.  
Because of this, it is suggested to always use `run_tool` if possible and
only manually `print` or `print_json` if necessary.

```python
from su6 import register_plugin, run_tool, state, print, print_json, RED_CIRCLE, GREEN_CIRCLE


# or: from su6.plugins import register, run_tool

@register_plugin
def echo():
    run_tool("echo", "with", "any", "args", "and", "options")


@register_plugin
def other_check():
    # when run_tool is not enough:
    if state.output_format == "json":
        print_json({"my": "data"})
    else:
        print(GREEN_CIRCLE, "great success!")

```