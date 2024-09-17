# Creating a Conda Environment

First, read the [Conda section](https://docs.mila.quebec/Userguide.html#conda) 
in Mila's documentation.

## Install Conda
If you still need to install a newer version of Conda, or if you want to install 
it on your personal computer:

```shell
make conda-install
```

## Environment Creation

Creating a Conda Environment is relatively straightforward with the makefile.

First, make sure the name of the environment has been updated in the 
[environment.yml file](../environment.yml) before running the following command:
```
make conda-create-env
```

## Conda Environment Activation

Once created, the environment must be activated:

```
conda activate <name_of_environment>
```