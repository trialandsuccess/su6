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