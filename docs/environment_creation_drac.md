
# Environment Creation and Management for DRAC

First things first, read the amazing [DRAC Python documentation](https://docs.alliancecan.ca/wiki/Python).

If you are also new to using Slurm clusters, please read 
[Getting started with DRAC](https://docs.alliancecan.ca/wiki/Getting_started) and 
[How to run jobs on the DRAC cluster](https://docs.alliancecan.ca/wiki/Running_jobs)

Below are simplified steps on how to create and manage a virtual environment on the 
DRAC cluster.

## Pre-built Python wheels and available modules

DRAC offers pre-build Python wheels for commonly used libraries. You can [consult them 
here](https://docs.alliancecan.ca/wiki/Available_Python_wheels).

However, many libraries, or newer versions of those libraries, are not available through 
those wheels.

For some libraries, like Pytorch or scientific libraries like Numpy, it can be 
better/simpler to use the pre-built versions.

For secondary or simple utility libraries, like `pytest`, `flake8` or `requests`, using 
versions from the pre-built wheels might not be critical or even preferred, as using 
the latest versions might be better overall.

While there are generally no problems with building your virtual environment with 
Pypi versions of the libraries on DRAC, sometimes this can lead to poorer performance and/or 
runtime errors. What's more, you also won't be available to build your environment 
inside your job ([like recommended here](https://docs.alliancecan.ca/wiki/Python#Creating_virtual_environments_inside_of_your_jobs)), 
unless you are working on Cedar, since its nodes have access to internet.

Do note that building your environment inside your job can help with some performance 
issues, but it is not required.

See [Managing Dependencies](#managing-dependencies-on-drac) below for more information 
on how to install dependencies from the local pre-built wheels.

**Important note**
While working on DRAC with pre-built Python wheels, the use of the `poetry.lock` file is not recommended; 
use [Tilde requirements](https://python-poetry.org/docs/dependency-specification/#tilde-requirements) 
instead to ensure reproducibility across different environments.

## Creating an environment on the DRAC cluster

The preferred method of creating a virtual environment for the DRAC cluster is 
with `virtualenv`

First, a python module is loaded by default on DRAC.

To see the available modules:
```
module avail python
```
To load a particular model (assuming 3.11.5 is available):
```
module load python/3.11.5
```

Then create the environment:
```
virtualenv <PATH_TO_ENV>
```

## Managing dependencies on DRAC

### The 3 choices

* Limit your self exclusively to DRAC's pre-built wheels, and code anything that's 
  missing yourself.
* Don't use pre-build wheels at all
* Use a mix of the 2.

The first 2 are pretty straight forward, but using a mix of dependency sources will 
require careful tracking and documentation.

Dependencies intended to be installed from pre-built wheels should go in the 
`[tool.poetry.dependencies]` section of the `pyproject.toml` file, while other 
dependencies should be added to an optional dependency group, which can then be installed 
with `poetry` ([See Adding Dependencies](../CONTRIBUTING.md#adding-dependencies))

For example, dependencies intended to be installed from DRAC's pre-build wheels should 
be added manually in the `[tool.poetry.dependencies]` section of the `pyproject.toml` file 
and installed using the `pip install -e . --no-index` command from the root of your 
repository root. 

For the other dependencies, an optional dependency group should be created in the 
`pyproject.toml` file. Make sure to [make the group optional](https://python-poetry.org/docs/managing-dependencies/#optional-groups).
Dependencies can be added to this group using the `poetry add --group <group_name> <dependency_name>` 
and can be installed with the command `poetry install --with <group_name>`

### Reproducibility

If using any dependencies from the DRAC pre-built wheels, you will still need to 
document the versions in a way that users outside DRAC can still use your code. 

For example : the requests library
*as of July 24th, 2024*

* Version available on DRAC : `2.31.0`
* Full version (what we see with `pip list`) : `requests==2.31.0+computecanada`
  * This version is obviously not available outside DRAC
* How to add it to the pyproject.toml:
  * If not on DRAC, you can use poetry to add it using `poetry add requests~2.31.0`
  * If on DRAC, add it manually to the pyproject.toml file under the `[tool.poetry.dependencies]` section : `requests = "~2.31.0"`

This will help ensure reproducibility between environments even when using pre-built 
wheel versions of Python dependencies.
