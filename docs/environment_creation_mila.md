# Creating a Virtual Environment on the Mila Cluster

On the Mila cluster, both `venv` and `virtualenv` can be used to create a virtual
environment.

First, load the python module:

```
module load python/3.10
```

Then, for `venv`:

```
python3 -m venv <PATH_TO_ENV>
```

or for `virtualenv`:

```
virtualenv <PATH_TO_ENV>
```

where `<PATH_TO_ENV>` is the path where the environment will be created. It normally
should be inside your project's folder (but ignored by git), and commonly named `
`.venv`. 

* _On a side note, `.env` is generally reserved for a text file listing 
  environment variables, used by various tools like `python-dotenv` and `docker compose`_

You can also make use of the following makefile targets:

```shell
# To create a .venv environment
make venv-create
```

```shell
# To remove the .venv environment
make venv-remove
```

You can then activate your environment using the following commandline:

```
source <PATH_TO_ENV>/bin/activate
```

If you used the `make venv-create` target, or create it at `<REPOSITORY_ROOT>/.venv`,
you can also use:

```shell
# To get the path for activation
make venv-activate
```

```shell
# To activate it
eval $(make venv-activate)
```

After the environment is created and activated, follow the [Poetry Instructions](../README.md#poetry)
