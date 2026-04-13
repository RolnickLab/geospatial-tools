# Python & QA Skill Instructions

\<primary_directive>
Your objective is to elevate research scripts into robust, maintainable, and type-safe software.
**MANDATE:** Apply the project-specific rules outlined below for all Python development and QA tasks.
\</primary_directive>

<context>
This project relies heavily on modern Python tooling and strictly enforced quality assurance.
- **Pre-commit is Central:** All QA tasks (linting, formatting, type checking) are orchestrated via `pre-commit`.
- **Environment & Build:** We use `uv` for package management and `hatchling` as the build backend (defined in `pyproject.toml`).
- **Task Automation:** We use `nox` for isolated test environments and task execution.
- **Makefile:** We use a makefile to automate and orchestrate most things in this project. Use `make targets` to discover the available targets.
</context>

<standards>
You MUST strictly adhere to the following project-specific Python standards:

### 1. QA & Tooling

- **QA Workflow:** ALWAYS run `make precommit` after making changes. Do not manually invoke linters unless debugging a specific `pre-commit` hook failure.
- **Tests:** Use `make test` to run tests.
- **Type Checking:** We use `mypy`. All new functions MUST have strict type hints.

### 2. Modern Project Standards

- **Strict Typing:** You MUST use type hints for ALL function arguments and return values (e.g., `def process(data: str | Any) -> pd.DataFrame`).
- **Filesystem Paths:** You MUST NEVER use `os.path`. ALWAYS use `pathlib.Path` for all file and directory manipulations.
- **Logging:** Use `structlog` for application flow. NEVER use `print()` for production code.
- **Data Structures:** ALWAYS use `@dataclass` or `pydantic` models for complex structures instead of untyped dictionaries.
- **Type Hints Format:** Always prefer X | Y format over Union[X, Y].
- **Docstrings:** Always add docstrings to your functions and classes. Use the Google standard for docstrings. Don't show types in docstrings.

### 3. Testing & Performance

- **Vectorization:** ALWAYS prefer vectorized operations (NumPy, Pandas, Polars, Xarray) over native Python `for` loops when processing geospatial data.
    </standards>

\<forbidden_patterns>

- ❌ **Bypassing Pre-commit:** Do not commit code that fails `pre-commit` checks. Fix the underlying linting or typing issue.
- ❌ **Global Mutable State:** You MUST NEVER define or mutate global variables to pass state between functions.
- ❌ **Magic Numbers/Strings:** You MUST NOT hardcode numeric constants. Extract them to Pydantic settings or config classes.
- ❌ **Bare Except Blocks:** You MUST NEVER use `except: pass` or `except Exception: pass`.
    \</forbidden_patterns>
