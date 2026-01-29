# Geospatial-tools

This repository is a collection of tools and scripts for geospatial use cases.

## 🐍 Python Version

This project uses **Python 3.11** and relies on a `Makefile` for standardized, reproducible commands.

You can read more about the makefile [here](.make/README.md).

## 📦 Package & Environment Management

- **Environment & Dependency Management:** **[uv](https://docs.astral.sh/uv/)** is the **recommended default** tool for fast, reliable dependency installation and virtual environment creation. It can be configured to use **[Poetry](https://python-poetry.org/docs/)** or `conda` via `Makefile.variables`.
- **Configuration:** Review the project-level configurations in [Makefile.variables](Makefile.variables) or set individual preferences in `Makefile.private`.

## ⚡ Quick Start

You can review your current active configurations using this command:

```bash
make info
```

You can list the available targets using this command:

```bash
make targets
```

### 🛠️ Tool-Specific Setup

Select your preferred development stack below. Ensure your `Makefile.variables` are configured to match your choice.

### Install System Tools

If needed, run the command corresponding to your chosen stack to install the necessary system tools.

<details open>
<summary><strong>Stack: uv (Default)</strong></summary>
```bash
make uv-install
```
</details>

### 📦 Installing the Project

Once your tools are configured and installed, run the universal install command. This will create the environment and install all dependencies defined in pyproject.toml.

```bash
make install
```

### 🔌 Activating the Environment

```bash
# Works for uv, poetry, and conda configurations
eval $(make uv-activate)
```

Alternatively, you can use `uv run <command>` directly:

```bash
uv run python <python_script.py>
# or
uv run pre-commit
```

## 📖 Project Usage

## 🌐 Environment & Portability Note

This template is designed for reproducibility using the `lock` files (`uv.lock`).

## 🛠️ Development Workflow

### Adding Dependencies

To add new dependencies, see the [Contributing guidelines](CONTRIBUTING.md#adding-dependencies).

### Pre-commit

This project uses `pre-commit` for automated code formatting and linting. The hooks are defined in `.pre-commit-config.yaml`.

- **Installation:** The `pre-commit install` command installs git hook that run automatically before each commit. It is run automatically when you run the `make install` command. It can also be installed manually with the `make install-precommit` command.
- **Automatic Fixes:** When you `git commit`, `pre-commit` will run. It will automatically fix many formatting issues (like `black`). If it makes changes, your commit will be aborted. Simply `git add .` the changes and commit again.
- **Manual Run:** You can run all checks on all files manually at any time:
    ```bash
    make precommit
    ```
- **Uninstalling:** To remove the git hooks:
    ```bash
    make uninstall-precommit
    ```

**Note about `markdown-link-check`**:

This pre-commit uses a tool called [markdown-link-check](https://github.com/tcort/markdown-link-check). It's a great tool to make sure all your links are up and accessible. Il you need to modify the exception list, say, because you are linking to a private repository and the check keeps failing, add it to the ignore patterns [here](.markdown-link-check.json)

## Other useful development targets

To run linting checks with `flake8`, `pylint`, `black`, `isort` and `docformatter`:

```bash
make check-lint
```

To fix linting with `autoflake`,`autopep8`,`black`, `isort`, `flynt` and `docformatter`:

```bash
make fix-lint
```

To run tests:

```bash
make test
```

### Nox

Behind the scenes, the targets in this section make use of the
[Nox automation tool](https://nox.thea.codes/en/stable/).

The configurations can be found in the [noxfile.py](noxfile.py) file.

For more information about how `nox` is used in this project, see

### Contributing

Please read and follow the [Contributing guidelines](CONTRIBUTING.md) for details on submitting code, running tests, and managing dependencies.
