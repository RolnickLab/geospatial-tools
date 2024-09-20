# Geospatial-Tools

## Requirements

This project has only been tested in a Linux (Debian based) environment and assumes
some basic tools for development are already installed.

The project uses a Makefile to automate most operations. If `make` is available on your 
machine there's a good chance this will work.

The following Makefile files should not be modified, but can be consulted:

* [Makefile](Makefile) : Orchestration of the different files
* [base.make](.make/base.make) : Shared utilities, project agnostic.

The following Makefile files are project or user specific:

* [Makefile.variables](Makefile.variables) : Shared project variables.
* [Makefile.targets](Makefile.targets) : Shared project targets.
* [Makefile.private](Makefile.private.example) : User specific variables and targets.

## Basic Information

The different targets and their description can be examined by executing the command
`make targets`

![](img/make_targets.png)

## Python Version

This project uses Python version 3.11

## Build Tool

This project uses Poetry as a build tool. Using a build tool has the advantage of 
streamlining script use as well as fix path issues related to imports.

## Installation

This project assumes environment management will be done with `Conda` or directly through
`Poetry`. 

* [Poetry](https://python-poetry.org/docs/basic-usage/)
* [Conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html)

While it is possible to manage the environment with, for example, pyenv or virtualenv, 
those specific use cases are not supported by the Makefile and require users to set up 
their own environments beforehand.

For detailed information about `Poetry` and `Conda`:

If you want to use something else than `Conda` or `Poetry` to manage environment isolation, 
it is recommended to follow 
[Poetry's guidelines on managing environments](https://python-poetry.org/docs/managing-environments/)

Poetry is not included in the [environment.yml](environment.yml), due to some possible problems
in compute cluster environments, but will be installed automatically if needed
by most `install` targets.

### Environment Management

You will need to create a virtual environment for your dependencies.

* [How to create a virtual environment for the Mila cluster](docs/environment_creation_mila.md)
* [How to create an environment for the DRAC cluster](docs/environment_creation_drac.md)
* [How to create a Conda environment](docs/conda_environment_creation.md)
* [Migrating to DRAC from another environment](docs/migrating_to_drac.md)

Do note that Conda is not available on the DRAC cluster, and there are some extra steps
to use Conda on the Mila cluster compared to a workstation.

####  Environment management choices

Environment management can become quite complicated. Using Conda allows a certain
ease of management since the Poetry installation is contained inside the created Conda 
environment.

However, some computing environments do not permit the use of Conda (like certain SLURM
clusters). This is why the `pipx` option for Poetry is also enabled. To 
install `pipx`, a user needs to have write access for the current environment, which is 
why, for compatibility reasons, we install it in a lightweight, standalone virtual environment.

*Disclaimer for those that already know a lot about Poetry...*

Yes, `Poetry` can manage environments directly, and there are a lot of other more advanced 
uses that are not explored in this repository. This is done on purpose, as an introduction 
to this tool in a context that is familiar for most users (i.e. creating virtual environments
with venv/virtualenv/conda). If you are comfortable with `Poetry` and especially its use 
on compute clusters, feel free to disregard the recommendations below. Just don't forget 
to document its use for the project!

### First Time User Quick Setup

#### Poetry

The easiest and quickest way to get up and running with Poetry.

Install pipx and Poetry and activate project environment :

```shell
make poetry-install-venv
```

**Or, if Poetry is already available:**

```shell
make poetry-create-env
```

Install package:

```shell
make install
```

#### Conda
The easiest and quickest way to get up and running with Conda.

Create Conda environment (will check for Conda and install it if not found):

```shell
make conda-create-env
```

Activate Conda environment (substitute with your <CONDA_TOOL> if something else 
than `conda`:

```
conda activate geospatial-tools
```

Install package:

```shell
make install
```

### In depth Environment and Install Targets

See [Environment and Install targets](docs/makefile_environment_targets.md)

## Useful targets for development

To run linting checks with `flake8`, `pylint`, `black` and `isort`:
```shell
make check-lint
```

To fix linting with `black`, `flynt` and `isort`:
```shell
make fix-lint
```

To run a `pre-commit` check before actually committing:
```shell
make precommit
```

To run tests:
```shell
make test
```

## Configurations
Configurations are in the [config/](configs) folder.

## Data

See [Data Readme](data/README.md)

## Contributing to this repository

See [Contributing guidelines](CONTRIBUTING.md)
