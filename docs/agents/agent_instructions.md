# Core agent instructions for all agents

## Mission

1. **Systems Orchestration:** Build robust, reproducible systems for ML and geospatial science. Focus on horizontal integration and end-to-end verification.

## Context

- **Environment:** This project is a **Laboratory**, not a strict production environment. We value experimentation, speed, and learning.
- **Outcome:** We aim for **Advanced Proofs of Concepts (POCs)** and **Prototypes** that are clean, documented, and easy for others to understand and take over. Remember: "Nothing is more permanent than a temporary solution."
- **Project level instructions:** These are your mandatory, project-level instructions. You need to consider these instructions for every task.

## 1. Core Mandate & Skills

- **Horizontal Integration:** Focus on system-wide flow. Define explicit contracts between modules. Prove the system works beyond unit tests.
- **Strategic Decomposition:** Break vague goals into atomic, verifiable milestones. Own the integration outcome.
- **Proactive Context Gathering:** Do not ask the user for information you can find yourself. Use your available search and file-reading tools (e.g., `grep_search` / `grep` / `file_search`, `glob` / `find`, `read_file` / `read_file_content` / `cat`) to understand existing data loaders, models, config patterns, and project standards (linting, testing frameworks).
- **Fail Gracefully & Teach Debugging:** When things break, do not just provide the fixed code. Explain *how* you found the bug, *why* it occurred, and *how* the user can diagnose similar issues in the future.
- **Keep it Simple:** Favor boring, simple, and readable code over overly clever, complex abstractions. The code must be understandable by a researcher who may not be a senior software engineer.
- **Intellectual Honesty:** Prioritize technical truth over agreement. Critically evaluate and challenge all requests, tasks, and assumptions. Propose superior alternatives with a clear explanation of technical trade-offs (e.g., performance, complexity, maintainability) and rationale.

## 2. Operational Workflow

- **Establish Baseline:** Identify the current state of the application.
- **Focused Execution:** Prioritize short, high-intent sessions with narrow, actionable objectives over broad, open-ended requests.
- **Durable Artifacts (The Written Plan):** Before writing implementation code for non-trivial tasks, you MUST create or update a `<TASK_DESCRIPTION>_PLAN.md` in `docs/agents/planning/<TASK_DESCRIPTION>/`.
- **Contract-First Design:** Explicitly define inputs/outputs and geospatial context (CRS, resolution) between pipeline stages BEFORE implementation. Enforce explicit data contracts (Pydantic Models, Dataclasses).
- **Atomic Versioning:** Use Git aggressively. Commit after every verified logical unit.
- **Incremental Review:** Implement exactly ONE step from the plan at a time. After successfully writing and validating code for a logical step, STOP and ask for validation before moving to the next step.

### Planning

Whenever you are doing a planning type task, read [docs/agents/instructions/planning.md](instructions/planning.md) before starting to work on a plan, a specification or creating tasks.

### Implementation

Whenever you are doing an implementation type task, read [docs/agents/instructions/software_dev.md](instructions/software_dev.md) before starting to work on a plan, a specification or creating tasks.

### Reviewing

Whenever you are doing a review type task, read [docs/agents/instructions/code_review.md](instructions/code_review.md)before starting to work on a plan, a specification or creating tasks.

## 3. Engineering Preferences

- **Python:** Strictly use `pathlib.Path`. Use `structlog` for JSON logging (never `print`). Prefer keyword arguments for complex function calls.
- **Geospatial Data:** Always explicitly handle CRS (`rasterio.crs.CRS.from_epsg()`). Use windowed reading for rasters > 100MB. Output as Cloud
    Optimized GeoTIFF (COG), Parquet (Snappy/Zstd), or Zarr.
- **Architecture:** Ensure ML/Data pipelines are idempotent.
- **Documentation:** Use Google Style docstrings and the Diátaxis framework.

## 4. Domain-Specific Guidelines

To assist with specific domains, specialized instruction files are available in `docs/agents/instructions`.
**Mandate:** You MUST read and apply the relevant project-specific context file when working within these domains. These files outline architectural constraints, preferred tools, and forbidden patterns for this specific repository.

| Domain                   | Project-Specific Context File                                                              |
| :----------------------- | :----------------------------------------------------------------------------------------- |
| **Planning**             | [**docs/agents/instructions/planning.md**](instructions/planning.md)                       |
| **Software Development** | [**docs/agents/instructions/software_dev.md**](instructions/software_dev.md)               |
| **Root Cause Analysis**  | [**docs/agents/instructions/root_cause_analysis.md**](instructions/root_cause_analysis.md) |
| **Review**               | [**docs/agents/instructions/review.md**](instructions/code_review.md)                      |
| **Knowledge Base**       | [**docs/agents/instructions/KNOWLEDGE.md**](instructions/KNOWLEDGE.md)                     |

## 4. Agent Behaviors, Memory & Tactics

- **Aggressive Checkpointing:** You MUST checkpoint between phases. After research, write findings to files. After planning, commit contracts.
- **Git as Memory:** You MUST use git aggressively. Commit after each logical unit.
- **Tribal Knowledge:** Consult, maintain and update `docs/agents/instructions/KNOWLEDGE.md`.
- **Token Efficiency:** Do not read entire files if search tools suffice.
- **Skill selection:** Once you identify the type of task you need to complete, **you must select and use the appropriate specialized agent skill listed in 4. Domain-Specific Guidelines**.

## 5. Forbidden Patterns (The "Please Don't" List)

Avoid these anti-patterns strictly, even in a rapid research context:

- ❌ **Vertical Myopia:** Optimizing one file while breaking integration.
- ❌ **Hardcoded Paths:** ALWAYS use `pathlib` and relative paths (or config files).
- ❌ **Plan Drift:** Changing architecture without updating `PLAN.md`.
- ❌ **Hardcoded Secrets:** NEVER put API keys/passwords in code. Use `.env`.
- ❌ **Silent Failures:** NEVER use bare `except: pass` or `except Exception: pass`. All caught exceptions must be logged or handled specifically.
- ❌ **Global State:** DO NOT use global variables to pass data between functions. It destroys reproducibility and debuggability.
- ❌ **Mega-Functions:** Break down functions longer than ~50-100 lines to ensure testability and readability.
- ❌ **Production `print()`:** Use `structlog` or standard `logging`. `print()` is only for temporary debugging.
- ❌ **Implied Contracts:** You MUST NOT pass raw, untyped dictionaries between components.
- ❌ **Skipping E2E Testing:** You MUST NOT declare complex integration "complete" without verifying data flow from start to finish.
