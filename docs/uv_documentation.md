# UV

`uv` is an alternative tool for dependency management, like `poetry` and `conda`.
It is blazingly fast and also comes with the possibility of easily getting access to
other versions of Python without tools like `pyenv`.

However, using `conda` together with `uv` can be very cumbersome and is not really recommended,
as the most useful dependency management features of `uv` will not work. If you really
want to use `uv` together with `conda`, see [using uv-pip](#note-about-using-pip-with-uv)

Therefore, if you require binary dependencies from `conda` (non-python dependencies likes
`cdo`, for example), it is recommended to use the classic `poetry` version of this
template, unless you have other ways of installing those dependencies.

This README is a quick and concise guide to get you started. Reading the
[official documentation](https://docs.astral.sh/uv/) is wholeheartedly recommended, as
you'll find yourself rapidly limited in what you can do.

## Getting started.

The only thing you have to do is start your project off from the template, like
[described here](https://github.com/RolnickLab/lab-basic-template/blob/main/README.md#initialization),
and then replace the contents of the
`pyproject.toml` file with the one present in this branch.

## Install UV

`uv` first needs to be installed.

The recommended way to install `uv` is with `pipx`.

On your personal computer, you can do the following:

```shell
pip install pipx
pipx ensurepath
pipx install uv
```

On compute clusters, like Mila and DRAC, you won't be able to use the default pip
available after loading a python module.

You will first need to create and activate a base virtual environment in which you have
write access.

For example, on the Mila cluster:

```
module load python/3.10
python3 -m venv ~/.pipx_env
source ~/.base_env/bin/activate
```

Next, `pipx` and `uv` can be installed using this new virtual environment's `pip`:

```
pip install pipx
pipx ensurepath
pipx install uv
```

The `pipx` way is pretty straightforward, but you can also install `uv`
many other ways, which are documented here:
[uv installation methods](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

## Setting up your environment

First download the version of python you want for your environment with `uv`:

```shell
# As an example, here is for python 3.12
uv python install 3.12
```

Then create your environment:

```shell
uv venv --python 3.12
```

### DRAC problems with uv venv

Creating an environment using `uv` on DRAC can create problems, most probably because
of the custom indexing and python wheels (exact reason has not been confirmed yet).

On the DRAC cluster, it is therefore preferred to load the python module and then create the environment
manually:

```shell
module load python/3.12
virtualenv --no-download .venv
source .venv/bin/activate
```

## Using uv with the makefile

First, make sure that the `uv` targets are activated, and that the `poetry` targets
are commented out in the [Makefile](../Makefile) main file.

To install `uv` on your system:

```shell
make uv-install
```

To create a new virtual environment:

```shell
make uv-create-env
```

To see the required command to activate your new environment:

```shell
make uv-activate
```

To migrate a `poetry` `pyproject.toml` file to uv:

```shell
make uv-migrate-from-poetry
```

For more information, see the `uv` target description with the following command:

```shell
make targets
```

To install the application:

```shell
make install
```

## Installing and managing dependencies manually

To first install the dependencies, after creating and activating the environment:

```shell
uv sync
```

To install the dev dependencies:

```shell
uv sync --group dev
```

To add a dependency:

```shell
uv add <dependency-name>
```

To add a dependency to the dev group:

```shell
uv add --group dev <dependency-name>
```

For more information about managing dependencies with `uv`, see the following
documentation [Managing dependencies with uv](https://docs.astral.sh/uv/guides/projects/#managing-dependencies)

### Installing DRAC custom wheels

To install dependencies like described in the
[DRAC documentation](https://docs.alliancecan.ca/wiki/Python#Creating_and_using_a_virtual_environment),
you can use the `--offline` flag, with either `sync` or `add`.

Ex:

```shell
uv sync --offline
```

You should also consider updating your `pyproject.toml` file with the following:

```toml
[tool.uv]
python-preference = "system"

## From https://docs.astral.sh/uv/reference/settings/#index-strategy:
## "Only use results from the first index that returns a match for a given package name."
## In other words: only get the package from PyPI if there isn't a version of it in the DRAC wheelhouse.
# index-strategy = "first-index"

## "Search for every package name across all indexes, exhausting the versions from the first index before
##  moving on to the next"
## In other words: Only get the package from PyPI if the requested version is higher than the version
## in the DRAC wheelhouse.
# index-strategy = "unsafe-first-match"

## "Search for every package name across all indexes, preferring the "best" version found.
##  If a package version is in multiple indexes, only look at the entry for the first index."
## In other words: Consider all versions of the package DRAC + PyPI, and use the version that best matches
## the requested version. In a tie, choose the DRAC wheel.
index-strategy = "unsafe-best-match"

[[tool.uv.index]]
name = "drac-gentoo2023-x86-64-v3"
url = "/cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3"
format = "flat"

[[tool.uv.index]]
name = "drac-gentoo2023-generic"
url = "/cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic"
format = "flat"

[[tool.uv.index]]
name = "drac-generic"
url = "/cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic"
format = "flat"
```

### Note about using pip with uv

While it is possible to use `pip`, you should try to avoid it when possible, for two reasons:

- If you do have to use `pip`, you should always use `uv pip`, as you will benefit
  from `uv`'s speed. Moreover, you could have another active `pip`, even if your `.venv` has
  been sourced; which will cause your use of `pip` to interact with another environment.
- Using `uv pip` does not update the `pyproject.toml` file, and does not update OR use
  the `uv.lock` file, which means you have to set your dependencies manually.

This last point is not necessarily a dealbreaker, and in some situations it might even
be necessary, like if you want to use `uv` with existing repositories that use
`requirements.txt` files.

You will, however, lose one of the most powerful features of `uv` that ensures your
environment is easily reproducible.

One more thing that is **very important** to note:

`uv pip` will always interact with the **active**
**environment**. This means that if you have your `.venv` environment in your repository,
but you also have, say, the base `conda` environment active, `uv pip` will interact
with the `conda` environment.

This is one way of working with both `conda` and `uv`,
but like mentioned above, you lose the ability to automatically manage your
`pyproject.toml` file and won't be able to use `uv.lock` file.

Consult the documentation to learn more about [uv's pip interfare](https://docs.astral.sh/uv/pip/).

## Using uv

To list the installed dependencies:

```shell
uv pip list
```

If you have sourced your `.venv`, you can use `python` and other tools through the
command line like you are used to.

You can also use the `uv run` command instead. Without the need to
manually source your `.venv` folder, this command allows access to your environment and
the installed dependencies - This is already taken into account in the Makefile targets:

```shell
# Execute a python script
uv run python scripts/my_python_script.py
```

```shell
# Execute the pre-commit check
uv run pre-commit run --all-files
```

For the development tool `nox`, you still have to be at the root of the repository, as
the command requires the presence of the `noxfile.py`:

```shell
# Don't forget to install the dev dependencies first with
# uv sync --group dev

uv run nox -s ruff-lint
```

## Converting to UV from poetry manually

You can easily convert your current `poetry` pyproject.toml file to `uv` with the following commands:

```shell
echo "Creating backup copy of current pyproject.toml file"
cp pyproject.toml pyproject.toml.poetry.backup 

echo "Migrating pyproject.toml file to use uv"
uvx migrate-to-uv --dependency-groups-strategy keep-existing
```
