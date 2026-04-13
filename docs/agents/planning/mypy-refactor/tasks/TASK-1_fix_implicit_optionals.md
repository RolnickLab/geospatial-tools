# Task: Fix Implicit Optionals

## Goal

Resolve all "implicit Optional" type errors (PEP 484) by explicitly typing parameters defaulting to `None` as `T | None`.

## Context & References

- **Plan:** `docs/agents/planning/mypy-refactor/mypy-refactor-plan.md`
- **Error Pattern:** `Incompatible default for parameter ... (default has type "None", parameter has type "T")`
- **Target Files:**
    - `src/geospatial_tools/raster.py` (Lines 248, 249)
    - `src/geospatial_tools/vector.py` (Lines 84, 123, 124, 269)
    - `src/geospatial_tools/radar/nimrod.py` (Line 20)

## Subtasks

1. **Modify `raster.py`:** Update `merge_raster_bands` parameters `merged_band_names` and `merged_metadata` to use `| None`.
2. **Modify `vector.py`:** Update `create_grid_from_bbox`, `create_grid_from_polygon`, and `save_grid_to_file` parameters (`crs`, `num_of_workers`) to use `| None`.
3. **Modify `nimrod.py`:** Update `extract_nimrod_from_archive` parameter `output_directory` to use `| None`.

## Requirements & Constraints

- Use modern Python union syntax (`T | None`) instead of `Optional[T]`.
- Ensure `None` checks are properly handled in the function bodies if they aren't already.

## Acceptance Criteria (AC)

- [x] `make mypy` no longer reports "implicit Optional" errors for these files.
- [x] Code remains functional and passes existing tests.

## Testing & Validation

- Run `make mypy` to verify fix.
- Run `make test` to ensure no regressions.

## Completion Protocol

- [x] Verify ACs.
- [x] `git add` changed files and `git commit -m "refactor(typing): fix implicit optionals in raster, vector, and nimrod"`
- [x] Update this document with completion status.
