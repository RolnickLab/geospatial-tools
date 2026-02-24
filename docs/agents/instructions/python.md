# Python Skill Instructions

\<primary_directive>
Your objective is to elevate research scripts into robust, maintainable, and type-safe software. You MUST enforce modern Python standards, clean architecture, and modularity, transforming "script-kiddie" code into production-ready research pipelines.
\</primary_directive>

<context>
Research code frequently suffers from tight coupling, global state, and lack of type safety, making it impossible to reuse or extend.
- **ETC (Easier To Change):** Good code is modular. Swapping a model or dataset should not require a massive rewrite.
- **Reliability:** Data pipelines must be idempotent (yielding the same result regardless of execution count).
- **Modernity:** Leverage strict typing, `dataclasses`, and `pathlib` to catch errors early.
</context>

<standards>
You MUST strictly adhere to the following Python standards:

### 1. Modern Project Standards

- **Strict Typing:** You MUST use type hints for ALL function arguments and return values (e.g., `def process(data: dict[str, Any]) -> pd.DataFrame`).
- **Data Structures:** ALWAYS use `@dataclass` or `pydantic` models for complex structures instead of untyped dictionaries.
- **Filesystem Paths:** You MUST NEVER use `os.path`. ALWAYS use `pathlib.Path` for all file and directory manipulations.
- **Logging:** Prefer standard `logging` or `structlog` over `print()` statements for application flow.

### 2. Architecture & Design

- **Single Responsibility Principle (SRP):** Functions must do one thing. If a function loads data, preprocesses it, AND trains a model, you MUST refactor it into separate, composed functions.
- **Dependency Injection:** Pass dependencies (configs, models, database connections) as arguments. NEVER rely on global variables.

### 3. Testing & Performance

- **Vectorization:** ALWAYS prefer vectorized operations (NumPy, Pandas, Polars) over native Python `for` loops when processing data.
- **Profiling First:** Do not optimize code blindly. Recommend `cProfile` or `line_profiler` to identify actual bottlenecks first.
    </standards>

\<reporting_format>
When conducting a code review or refactoring, present your findings using this structure:

| Severity             | Category     | Issue                | Why and How to Fix                                                   |
| :------------------- | :----------- | :------------------- | :------------------------------------------------------------------- |
| **CRITICAL**         | Security     | `eval(user_input)`   | Extremely dangerous. Replace with `ast.literal_eval` or JSON parser. |
| **HIGH**             | Architecture | Tight Coupling       | Hardcoded dataset paths inside model class. Inject path as config.   |
| **MEDIUM**           | Typing       | Missing Type Hints   | Unclear API contract. Add `-> list[str]` to function signature.      |
| **LOW**              | Style        | `os.path.join` usage | Deprecated paradigm. Replace with `pathlib.Path() / ...`.            |
| \</reporting_format> |              |                      |                                                                      |

\<forbidden_patterns>

- ❌ **Global Mutable State:** You MUST NEVER define or mutate global variables to pass state between functions.
- ❌ **Magic Numbers/Strings:** You MUST NOT hardcode numeric constants or configuration strings deep in the logic. Extract them to constants or configuration objects.
- ❌ **Bare Except Blocks:** You MUST NEVER use `except: pass` or `except Exception: pass`. All caught exceptions must be logged or handled specifically.
- ❌ **Deep Nesting:** You MUST refactor code that exceeds 3-4 levels of indentation (e.g., deeply nested `for` and `if` blocks) into helper functions.
    \</forbidden_patterns>
