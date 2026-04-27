# TASK-2: Create Sentinel3Search Wrapper Class

## Goal

Implement `Sentinel3Search` extending `AbstractStacWrapper` for automated STAC queries on Planetary Computer.

## Context & References

- **Source Plan**: `docs/agents/planning/add-sentinel3/add-sentinel3-plan.md`
- **Relevant Specs**: `docs/agents/planning/add-sentinel3/add-sentinel3-spec.md`
- **Existing Code**: `src/geospatial_tools/stac/core.py`, `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` (for reference)

## Subtasks

1. [ ] Create `src/geospatial_tools/stac/planetary_computer/sentinel_3.py`.
2. [ ] Implement `Sentinel3Search` inheriting from `AbstractStacWrapper`.
3. [ ] Implement `filter_by_orbit_state` and `_build_collection_query` methods.
4. [ ] Override `download` method to normalize bands to lowercase (like S1).
5. [ ] Write unit tests in `tests/test_planetary_computer_sentinel3.py`.

## Requirements & Constraints

- Must adhere to the Facade + Proxy pattern defined in `AbstractStacWrapper`.
- S3 bands on Planetary Computer require lowercase asset keys during download.
- Filtering by `ORBIT_STATE` must invalidate the client state.

## Acceptance Criteria (AC)

- [ ] AC 1: Instantiates with `OLCI_WFR` by default if no collection provided.
- [ ] AC 2: `filter_by_orbit_state` updates internal state and invalidates caches.
- [ ] AC 3: `_build_collection_query` builds correct `eq` (single) or `in` (multiple) dictionary structures for `sat:orbit_state`.
- [ ] AC 4: Test coverage covers initialization, filtering, query building, and lowercase band handling.

## Testing & Validation

- **Command**: `make test`, `make pylint`, `make mypy`, `make precommit`
- **Success State**: All QA steps complete without errors.
- **Manual Verification**: Run full suite to ensure zero side-effects on S1/S2 behavior.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: implement Sentinel3Search wrapper"`
6. [ ] Update this document: Mark as COMPLETE.
