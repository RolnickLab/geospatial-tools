# Poetry Documentation

## Considerations when using Poetry in a Compute Cluster environment

### Version concerns on DRAC

As of this writing (February 2025), the newest available version on DRAC for `poetry` is
`2.0.1+computecanada`, and is the version causing problems.

Newer versions of `poetry`, `>=2.0.0` are raising errors when trying to
resolve dependencies when installing projects and adding new dependencies.

If you encounter such issues, please try reinstalling `poetry` at a lesser version:
`pipx install 'poetry<2.0.0'`, or newer, non-computecanada versions if available.

### Poetry Cache Management

Whether installing `poetry` as a standalone tool or in a conda environment, cache
management is an important consideration in a shared compute cluster.

If you maintain the default configuration, `poetry`'s cache is located
somewhere in your `$HOME` folder, ex. `$HOME/.cache/pypoetry`.

The cache can get big quite fast. It is also something that can change a lot
over time, which is not ideal for drive that are backed up regularly, like `/projects/`.

Since a cache is supposed to be temporary by nature, and easy to recreate
(most of the time), it can make sense to move the cache to `$SCRATCH`,
as there are very few and limited consequences if it ends up being deleted by the
`purge` policies.

To see current configs and current `cache-dir` path :

```bash
poetry config --list
```

There are a few options available in managing `poetry`'s cache in a cluster environment

### Option 1: move the cache

To set a new cache path:

```bash
poetry config cache-dir /PATH/TO/SCRATCH/.cache/pypoetry
```

### Option 2: clean your caches periodically, or disable them

You can view the existing caches (typically `PyPI` and `_default_cache`) :

```bash
poetry cache list
```

You can clean your caches directly:

```bash
poetry cache clear <CACHE_NAME> --all
```

Or disable them altogether:

```bash
poetry cache clear <CACHE_NAME> --no-cache
```

### Option 3: manually skip cache when installing dependencies

When adding dependencies :

```bash
poetry add <DEPENDENCY_NAME> --no-cache
```

When installing a project:

```bash
poetry install --no-cache
```
