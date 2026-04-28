# Task: Address Missed Mypy Errors

## Goal

Resolve the remaining mypy errors that were not covered by Tasks 1-4, ensuring 100% type checking coverage.

## Context & References

- **Plan:** `docs/agents/planning/mypy-refactor/mypy-refactor-plan.md`
- **Target Files:**
    - `src/geospatial_tools/download.py` (Line 32)
    - `src/geospatial_tools/vector.py` (Lines 113, 141, 338)
    - `tests/test_copernicus.py` (Line 144)

## Subtasks

1. **Fix `download.py`:** Update type checking or argument for `unzip_file` (handle `Path | None`).
2. **Fix `vector.py`:** Add correct type annotations for `properties` dict, narrow type of `bounding_box` in `create_grid_from_bbox`, and fix return type for `save_grid_to_file`.
3. **Fix `test_copernicus.py`:** Update `bbox` argument to use a tuple `(float, float, float, float)`.

## Requirements & Constraints

- Follow modern typing conventions (`T | None`, `pathlib.Path`, etc.).
- Ensure no runtime regressions.

## Acceptance Criteria (AC)

- [x] `make mypy` passes with 0 errors.

## Testing & Validation

- Run `make mypy`.
- Run `make test`.

## Completion Protocol

- [x] Verify ACs.
- [x] `git add` changed files and `git commit -m "refactor(typing): fix missed mypy errors across various modules"`
- [x] Update this document with completion status.
