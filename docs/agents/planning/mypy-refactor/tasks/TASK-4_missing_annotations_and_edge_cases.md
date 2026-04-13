# Task: Address Missing Annotations and Edge Cases

## Goal

Provide missing type annotations for dictionaries/lists and fix specific logic-related type errors.

## Context & References

- **Plan:** `docs/agents/planning/mypy-refactor/mypy-refactor-plan.md`
- **Error Patterns:** `Need type annotation for "params"`, `Missing return statement`, `Incompatible return value type`, `Unsupported right operand type for in`.
- **Target Files:**
    - `src/geospatial_tools/utils.py` (Lines 49, 96, 165, 170)
    - `src/geospatial_tools/raster.py` (Lines 178, 181, 312)
    - `src/geospatial_tools/planetary_computer/sentinel_2.py` (Lines 69, 70, 71, 213, 301, 308)
    - `src/geospatial_tools/stac.py` (Lines 234, 657)

## Subtasks

1. **Fix `utils.py`:** Add annotation for `params`, fix `logging_level` assignment, and handle `dataset_crs` type checks properly.
2. **Fix `raster.py`:** Fix `gdf` indexing (ensure it's a GeoDataFrame), fix `zip` argument type, and correct return type of `merge_raster_bands`.
3. **Fix `planetary_computer/sentinel_2.py`:** Add annotations for result attributes, add missing return statement in `sentinel_2_complete_tile_search`, and fix unpacking error in `future.result()`.
4. **Fix `stac.py`:** Handle `self.bands` being `None` in membership checks and fix `sortby` parameter type.

## Requirements & Constraints

- Avoid `Any` where possible; use specific types or `TypeVar` if needed.
- Ensure `future.result()` unpacking matches the actual return type of the submitted function.

## Acceptance Criteria (AC)

- [ ] `make mypy` passes with 0 errors.
- [ ] All logical fixes are verified by tests.

## Testing & Validation

- Run `make mypy`.
- Run `make test`.
- Run `make precommit`.

## Completion Protocol

- Verify ACs.
- `git add` changed files and `git commit -m "refactor(typing): fix missing annotations and specific edge cases"`
- Update this document with completion status.
