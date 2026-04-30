# TASK-0: Project Prerequisites — Markers & Dependencies

Maps to **Plan Step 0**.

## Goal

Resolve pre-existing project hygiene gaps that would otherwise contaminate every test run and obscure dependency declaration for the new Landsat module.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§3, §4 step 0)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2, §5)

## Subtasks

1. Add `[tool.pytest.ini_options]` block to `pyproject.toml` registering markers:
    - `integration`: marks tests that hit live STAC search endpoints (no asset bytes downloaded).
    - `online`: marks tests that require credentials and download asset bytes.
        Existing tests already use both markers (e.g. `tests/test_copernicus.py:112`, `tests/test_planetary_computer_sentinel2.py:6`) but they are unregistered, producing `PytestUnknownMarkWarning` on every run.
2. Add `requests` as explicit top-level dependency in `[project] dependencies` in `pyproject.toml`. Currently transitive via `boto3`; the new auth code uses it directly and must declare it.
3. Run `uv sync` (or equivalent) to refresh lockfile.
4. Run `make test` and confirm marker warnings disappear.

## Requirements & Constraints

- Do not pin a specific `requests` version unless project conventions require it; use `>=2.32.0` as a safe floor.
- Do not change other tooling configuration (mypy/ruff/black) in this task.
- Do not modify any source code outside `pyproject.toml` and lockfile.

## Acceptance Criteria (AC)

- `pytest --collect-only` produces no `PytestUnknownMarkWarning` for `integration` or `online` markers.
- `requests` appears in `[project] dependencies` of `pyproject.toml`.
- `make precommit`, `make pylint`, `make test`, and `make mypy` pass without regressions.

## Completion Protocol

1. All ACs met. [DONE]
2. Tests pass without regressions. [DONE]
3. Code passes linting and type-checking. [DONE]
4. Commit work: `git commit -m "chore: task 0 - register pytest markers and declare requests dependency"` [DONE]
5. Update document: Mark as COMPLETE. [COMPLETE]
