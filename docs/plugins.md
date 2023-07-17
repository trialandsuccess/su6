# Plugins

To add more checkers or other functionality, `su6` can be extended with plugins.  
You can use [this template repository](https://github.com/robinvandernoord/su6-plugin-template) to get some boilerplate
code, and checkout [the demo plugin](https://github.com/robinvandernoord/su6-plugin-demo) for more example code.

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


@register(
    add_to_all=True, # will include this command when running `su6 all`.
    name="third" # extra keyword arguments will be forwarded to Typer's @app.command
)  
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

## Plugin Config

A plugin can also load plugin-specific config from the user-defined config file (usually pyproject.toml).
This config works similar to the `state.config` of this module.
Keys are typed, and will throw a type error if the type in the toml file does not match with the annotation.
This behavior can be disabled by passing `strict=False` to the `@register` call.
`add_to_all` and `add_to_fix` can be used to extend the functionality of `su6 all` and `su6 fix` respectively.

Default config can be updated with for example command arguments with the `.update` method.
If a value is `None`, the key will NOT be updated to preserve defaults. Other Falsey values will overwrite the defaults.

Config Classes are Singletons, so creating a new instance of a config class will always have the same data as other
instances.

```toml
[project.entry-points."su6"]
demo = "su6_plugin_demo.cli"

# ...
[tool.su6.demo]
some = "config"

[tool.su6.demo.extra]
more = ["config", "here"]

[tool.su6.demo.untyped]
number = 3
```

```python
import contextlib
from su6.plugins import register, PluginConfig


@register
class MyConfig(PluginConfig):
    some: str


@register(config_key="demo.extra")
class ExtraConfig(PluginConfig):
    more: list[str]


@register(with_state=True, strict=False, config_key="demo.untyped")
class StateConfig(PluginConfig):
    number: str


my_config = MyConfig()
extra_config = ExtraConfig()
state_config = StateConfig()


# note: config is not set up at this moment yet,
# it is only available in a command since the user can define `--config` 
# and those arguments are parsed after importing plugin modules.

@register
def command(optional_argument: str = None):
    assert my_config.some == "config"
    assert extra_config.more == ["config", "here"]
    assert state_config.state

    my_config.update(some="new!")
    assert my_config.some != "config"

    assert MyConfig() is my_config

    # will update 'some' if optional_argument is not None
    my_config.update(some=optional_argument)

    with contextlib.suppress(KeyError):
        # will error since new_key is not defined in MyConfig:
        my_config.update(new_key=optional_argument)

    # will work and create a new (untyped) property:
    my_config.update(new_key=optional_argument, strict=False)

```