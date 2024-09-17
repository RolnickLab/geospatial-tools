# Environment and Installation Related Makefile Targets

## Poetry targets

There are 2 possibilities available in how to manage `Poetry` if it is not already
configured on your system.

**It is not recommended to install `Poetry` in the same environment that will be managed
by `Poetry`; It should be installed by `Conda` (as in, `conda install poetry`) or 
on the system using `pipx`, in order to minimize dependency conflicts.**

The following target will first try to install `Poetry` in the active `Conda` 
environment; if it can't find `Conda`, it will proceed to install via `pipx`

```shell
make poetry-install-auto
```

To install `Poetry` using `Conda`:

```shell
make conda-poetry-install
```

Using `pipx` will instead allow environment management directly with `Poetry`. The
following target will also make `Poetry` use a Python 3.11 environment for this
project.

```shell
make poetry-install-venv
```

This will also create a virtual environment managed by `Poetry`.

A standalone environment can also be created later using the `make poetry-create-env`
command, and removed with the `make poetry-remove-env` command.

Information about the currently active environment used by Poetry, 
whether Conda or Poetry, can be seen using the `make poetry-env-info` command.

Both install methods can also be cleaned up:

```shell
make conda-poetry-uninstall
```
or
```shell
make poetry-uninstall-pipx
```

**Important note!**

If you have an active `Conda` environment  and install `Poetry` using `pipx`,
you will have to use `poetry run python <your_command_or_script_path>` instead of 
`python <your_command_or_script_path>`, (which is normal when using Poetry) as 
`python` will use Conda's active environment.

## Conda Targets

If you need or want to install Conda:
```shell
make conda-install 
```

To create the conda environment:
```shell
make conda-create-env
```

To remove the conda environment:
```shell
make conda-clean-env
```

Make sure to activate the configured environment before installing.

## Install targets

**All `install` targets will first check if `Poetry` is available and try to install
it with the `make poetry-install-auto` target.**

To install the package, development dependencies and CLI tools (if available):
```shell
make install
```

To install only the package, without development tools:
```shell
make install-package
```
