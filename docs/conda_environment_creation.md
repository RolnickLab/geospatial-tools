# Creating a Conda Environment

First, read the [Conda section](https://docs.mila.quebec/Userguide.html#conda)
in Mila's documentation.

To make full use of the Conda makefile target, make sure to define the variables found
in [Makefile.variables](../Makefile.variables) appropriately, and ensure that
the `CONDA_ENVIRONMENT` variable lines up with the name defined in the
[environment.yml](../environment.yml) file.

## Install Conda

**Warning!!!**

**Unless absolutely necessary, it is not recommended to install a local
version of Conda when using a compute cluster like Mila or DRAC. You should only
install Conda if you will be working directly on your local machine.**

If you need to install a newer version of Miniconda, or if you want to install
it for the first time on your personal computer:

```shell
make conda-install
```

### Alternative : Mamba

You can also choose to install [micromamba](https://mamba.readthedocs.io/en/latest/index.html)
as an alternative or a complement to miniconda.

If you do install mamba, make sure to create a renamed copy of
[Makefile.private.example](../Makefile.private.example) -> `Makefile.private` and set
the `CONDA_TOOL` variable to `CONDA_TOOL := micromamba` so the Makefile can use it.

```shell
make mamba-install
```

## Environment Creation

Creating a Conda Environment is relatively straightforward with the makefile.

First, make sure the name of the environment has been updated in the
[environment.yml file](../environment.yml) before running the following command:

```shell
make conda-create-env
```

## Conda Environment Activation

Once created, the environment must be activated:

```
# If using micromamba, replace 'conda' with 'micromamba'
conda activate <name_of_environment>
```

You can use this command to see the command as configured for the project:

```shell
make conda-activate
```

You can also use the eval command to activate the environment:

```shell
eval $(make conda-activate)
```
