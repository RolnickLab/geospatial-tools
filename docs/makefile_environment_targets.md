# Environment and Installation Related Makefile Targets

## Venv targets

There are three targets in the makefile to help with streamling classic python virtual
environments.

```shell
# Create a virtual environment at <REPOSITORY_ROOT>/.venv/
make venv-create
```

```shell
# Get the path to activate the virtual environment created at <REPOSITORY_ROOT>/.venv/
make venv-activate
```

```shell
# Activate the virtual environment using the path returned by 'make venv-activate'
eval $(make venv-activate)
```

```shell
# Remove a virtual environment at <REPOSITORY_ROOT>/.venv/
make venv-remove
```

## Poetry install targets

### Installing poetry

There are two possibilities available to manage `poetry` if it is not already
configured on your system.

**It is generally not recommended to install `poetry` in the same environment that will
be managed by `poetry`; It is preferable to install it on the system using `pipx`,
to minimize dependency conflicts.**

That being said, having `poetry` installed in a `conda` environment, and using `poetry`
to manage that same `conda` environment is not the end of the world and is an acceptable
workaround for some projects.

See the [official documentation on how to install poetry](https://python-poetry.org/docs/#installation)
for more details if you prefer to install `poetry` manually.

The following target will install `poetry` interactively, asking questions along the way:

```shell
make poetry-install
```

To install `poetry` in a non-interactive way, you can instead use this target:

```shell
make poetry-install-auto
```

The above target will try to install `poetry` according to the `DEFAULT_POETRY_INSTALL_ENV`
Makefile variable; if it's not defined, installation of `poetry` will proceed via `pipx`.

The `DEFAULT_POETRY_INSTALL_ENV` variable can be set in your local `Makefile.private` file.
If you don't have one, this file can be created by copying from the
[Makefile.private.example](../Makefile.private.example) file.

If you know exactly how you want to install `poetry`, you have three options:

```shell
# This will install poetry using pipx. If pipx needs to be installed, it will be installed
# using the locally available pip. This does not work on the different compute clusters.
make poetry-install-local
```

```shell
# This will install poetry with pipx. If pipx needs to be install, it will be installed
# in a newly created virtual environment in $HOME/.pipx_venv.
make poetry-install-venv
```

```shell
# This will install poetry in the projects conda environment, along side all other python
# dependencies.
make conda-poetry-install
```

Both install methods have their respective cleanup targets:

```shell
make poetry-uninstall
```

```shell
make conda-poetry-uninstall
```

You can also use `make poetry-uninstall-pipx` or `make poetry-uninstall-venv` to also
remove the `pipx` library and the `pipx` virtualenv, respectively, depending on how you
chose to install `pipx` and `poetry`.

### Environment creation with Poetry

Using `poetry` to create a virtual environment is different from creating one using `venv`
or `virtualenv`, as they are centralized and managed by `poetry`.

A `poetry` virtual environment can be created using the following target:

```shell
make poetry-create-env
```

and be removed with:

```shell
make poetry-remove-env
```

Information about the currently active environment used by Poetry,
whether Conda or Poetry, can be seen using:

```shell
poetry-env-info
```

## Conda Targets

### Installing Conda

If you need or want to install Conda:

```shell
make conda-install 
```

```shell
# Alternatively, you can also install micromamba.
make mamba-install 
```

On the Mila cluster, it is preferable to use the available `anaconda` module instead:

```shell
module load anaconda/3
```

### Environment creation

To create the conda environment:

```shell
make conda-create-env
```

To remove the conda environment:

```shell
make conda-clean-env
```

Make sure to activate the configured environment before using the install targets.

## Install targets

**All `install` targets will first check if `Poetry` is available and try to install
it with the `make poetry-install-auto` target.**

To install the package, development dependencies, and CLI tools (if available):

```shell
make install
```

To install only the package, without development tools:

```shell
make install-package
```
