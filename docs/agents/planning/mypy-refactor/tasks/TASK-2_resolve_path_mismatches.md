# Task: Resolve Path vs String Mismatches

## Goal

Ensure consistent use of `pathlib.Path` for file system operations and resolve operator errors (e.g., `/` on strings).

## Context & References

- **Plan:** `docs/agents/planning/mypy-refactor/mypy-refactor-plan.md`
- **Error Pattern:** `Incompatible types in assignment`, `Unsupported left operand type for / ("str")`, `Argument X to "Y" has incompatible type "str"; expected "Path"`
- **Target Files:**
    - `scripts/resample_tiff_raster.py` (Lines 44, 45, 46, 48, 68)
    - `src/geospatial_tools/planetary_computer/sentinel_2.py` (Lines 398, 406, 414)
    - `scripts/sentinel_2_search_and_process/product_search.py` (Lines 156, 157)
    - `scripts/sentinel_2_search_and_process/download_and_process.py` (Lines 56, 68, 69)

## Subtasks

1. **Fix `resample_tiff_raster.py`:** Update variable type hints and ensure `Path` objects are used for division and function calls.
2. **Fix `planetary_computer/sentinel_2.py`:** Ensure `output_dir` is treated as a `Path` before using the `/` operator.
3. **Fix `product_search.py` & `download_and_process.py`:** Update default arguments and parameter types to accept/use `Path` where appropriate.

## Requirements & Constraints

- Strictly use `pathlib.Path`.
- Use `Path.joinpath()` or the `/` operator only on `Path` objects.

## Acceptance Criteria (AC)

- [x] `make mypy` no longer reports path-related errors in these files.
- [x] Scripts execute successfully without `TypeError` or `AttributeError`.

## Testing & Validation

- Run `make mypy` to verify fix.
- Run relevant scripts or integration tests (if available) to confirm file path handling works.

## Completion Protocol

- [x] Verify ACs.
- [x] `git add` changed files and `git commit -m "refactor(typing): resolve path vs string mismatches"`
- [x] Update this document with completion status.
