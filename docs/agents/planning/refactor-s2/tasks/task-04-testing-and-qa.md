# TASK-04: Integration Testing & End-to-End Validation

## Goal

Verify the structural integrity, behavioral correctness, and API integration of the refactored Facade pattern across both `Sentinel1Search` and `Sentinel2Search`. Ensure complete compliance with the project QA pipelines.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor-s2/refactor-s2-plan.md`
- **Relevant Specs**: `docs/agents/planning/refactor-s2/refactor-s2-spec.md`
- **Existing Code**:
    - `tests/test_planetary_computer_sentinel1.py`
    - `tests/test_planetary_computer_sentinel2.py` (or create if missing)

## Subtasks

1. [ ] Update/write integration tests (`@pytest.mark.integration`) for both `Sentinel1Search` and `Sentinel2Search` that:
    - Connect to the live PC STAC API.
    - Pin a specific bounding box and date range.
    - Chain multiple builder methods (e.g., optical filters for S2, radar filters for S1).
    - Assert valid `pystac.Item` properties are returned.
2. [ ] Verify that legacy searches using `BestProductsForFeatures` continue to pass without regression.
3. [ ] Run `make pylint`, `make mypy`, `make precommit`, and `make test`. Resolve any QA failures across the codebase.

## Requirements & Constraints

- Integration tests must be explicitly marked with `@pytest.mark.integration` to prevent network requests during standard local testing if configured that way.

## Acceptance Criteria (AC)

- [ ] AC 1: Live integration tests retrieve correct data reflecting chained filters for both S1 and S2.
- [ ] AC 2: Legacy S2 searches function without regression.
- [ ] AC 3: `make test` runs without failures.
- [ ] AC 4: Code passes all project QA pipelines (`make pylint`, `make mypy`, `make precommit`).

## Testing & Validation

- **Command**: `make test`, `make mypy`, `make pylint`, `make precommit`
- **Success State**: All QA tools exit with code 0.
- **Manual Verification**: Ensure the integration tests pass against the live STAC endpoint.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Commit work: `git commit -m "test: task 04 - end-to-end integration and QA validation"`
5. [ ] Update this document: Mark as COMPLETE.
