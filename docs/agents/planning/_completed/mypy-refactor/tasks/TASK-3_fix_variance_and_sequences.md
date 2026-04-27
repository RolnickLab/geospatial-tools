# Task: Fix Sequence and List Variance

## Goal

Replace `list[T]` with `Sequence[T]` in function arguments to allow covariant types and resolve variance-related errors.

## Context & References

- **Plan:** `docs/agents/planning/mypy-refactor/mypy-refactor-plan.md`
- **Error Pattern:** `"list" is invariant ... Consider using "Sequence" instead, which is covariant`
- **Target Files:**
    - `src/geospatial_tools/stac.py` (Lines 272, 360, 373)
    - `src/geospatial_tools/utils.py` (Line 236)
    - `src/geospatial_tools/planetary_computer/sentinel_2.py` (Line 238)
    - `tests/test_copernicus.py` (Line 164)

## Subtasks

1. **Modify `stac.py`:** Update function signatures (`merge_raster_bands`, etc.) to accept `Sequence[Path | str]` instead of `list`.
2. **Modify `utils.py`:** Update return type or internal typing of `unzip_file` / `extract_nimrod_from_archive` (or related) to use `Sequence`.
3. **Modify `planetary_computer/sentinel_2.py`:** Update `date_ranges` parameter to use `Sequence`.
4. **Modify `test_copernicus.py`:** Ensure test data types match expected sequences.

## Requirements & Constraints

- Import `Sequence` from `collections.abc` (Python 3.9+).
- Do not use `Sequence` for return types unless the function truly returns an immutable sequence; prefer `list` for returns if caller expects mutability, but handle the variance in the *argument* of the receiving function.

## Acceptance Criteria (AC)

- [x] `make mypy` no longer reports variance errors for these files.
- [x] Code functionality remains unchanged.

## Testing & Validation

- Run `make mypy`.
- Run `make test`.

## Completion Protocol

- [x] Verify ACs.
- [x] `git add` changed files and `git commit -m "refactor(typing): fix sequence and list variance issues"`
- [x] Update this document with completion status.
