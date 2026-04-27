# TASK-01: Isolate Legacy Code (BestProductsForFeatures)

## Goal

Sever the inheritance between `BestProductsForFeatures` and `AbstractSentinel2` to isolate legacy logic and unblock the refactor of the underlying STAC query base classes. This enforces the "Composition over Inheritance" principle and eliminates tight coupling.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor-s2/refactor-s2-plan.md`
- **Relevant Specs**: `docs/agents/planning/refactor-s2/refactor-s2-spec.md`
- **Existing Code**: `src/geospatial_tools/stac/planetary_computer/sentinel_2.py`

## Subtasks

1. [x] Remove `AbstractSentinel2` from `BestProductsForFeatures` class inheritance.
2. [x] Remove the `super().__init__(...)` call from `BestProductsForFeatures.__init__` (currently at `sentinel_2.py:173`). Move all referenced state variables (`date_ranges`, `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`, `error_results`) directly into `BestProductsForFeatures.__init__`.
3. [x] Copy the `create_date_ranges` method from `AbstractSentinel2` directly into `BestProductsForFeatures`.
4. [x] Ensure `BestProductsForFeatures` does not depend on any state outside of its own instance.
5. [x] Replace `print(error)` with `LOGGER.warning(str(error))` in `sentinel_2_complete_tile_search` (`sentinel_2.py:327`). This `print` call will cause `make pylint` and `make precommit` to fail in task-04.

## Requirements & Constraints

- The `BestProductsForFeatures` class and associated module-level helper functions must function exactly as before.
- No changes should be made to the underlying logic of `BestProductsForFeatures.find_best_complete_products` or related execution logic.
- Code must remain type-safe according to `make mypy`.

## Acceptance Criteria (AC)

- [x] AC 1: `BestProductsForFeatures` no longer inherits from `AbstractSentinel2` and contains no `super()` calls.
- [x] AC 2: `BestProductsForFeatures` manages its own `date_ranges`, `max_cloud_cover`, and `max_no_data_value` state.
- [x] AC 3: `sentinel_2_complete_tile_search` uses `LOGGER.warning(str(error))` instead of `print(error)`.
- [x] AC 4: `make test` passes without regression for any existing legacy Sentinel 2 searches.

## Testing & Validation

- **Command**: `make test`, `make mypy`, `make pylint`
- **Success State**: All tests pass, zero type/linting errors introduced.
- **Manual Verification**: Review `BestProductsForFeatures` to ensure no residual super() calls or inherited properties are used.

## Completion Protocol

1. [x] All ACs are met.
2. [x] Tests pass without regressions.
3. [x] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [x] Commit work: `git commit -m "refactor: task 01 - isolate BestProductsForFeatures from AbstractSentinel2"`
5. [x] Update this document: Mark as COMPLETE.

**STATUS: COMPLETE**
