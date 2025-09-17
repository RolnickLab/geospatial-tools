# Nox sessions

The configurations can be found in the [noxfile.py](../noxfile.py) file.

Feel free to modify the contents of existing sessions, as well as add new ones for your
project.

However, it would be best to avoid renaming existing ones as the Makefile expects the
current session names unless you also plan to override the existing Makefile targets
that use them.

With the `nox` tool, individual _commands_ are called sessions, and can be executed using
the following syntax:

```shell
nox -s <session_name>
```

- Main `nox` sessions:

  - No session specified; executing `nox` : Runs the pre-commit configuration
  - `check` Runs all checks on the code base without modifying the code
  - `fix` : Runs the autoflake, autopep8, black, isort, docformatter and flynt tools on the code base
  - `flake8` : Runs the `flake8` linter
  - `autoflake` : Run the `autoflake` lint fixer to remove unused imports and variables
  - `autopep8` : Run the `autopep8` lint fixer to automatically fix most other `flake8` warnings
  - `black` : Runs the code formatter
  - `isort` : Runs the import sorter
  - `flynt` : Runs the `f-string` formatter
  - `mdformat` : Runs the markdown formatter
  - `docformatter` : Runs the docstring formatter
  - `test` : Runs tests found in the `tests/` folder with `pytest`

- `ruff` - Experimental sessions:

  - `ruff-lint` : Check lint using the `ruff` linter. This linter is stricter
    than `flake8`, but less than `pylint`
  - `ruff-fix` : Check lint using the `ruff` linter and automatically fix the
    warnings that can be fixed by `ruff`
  - `ruff-format` : Format the code using the `ruff` formatter
