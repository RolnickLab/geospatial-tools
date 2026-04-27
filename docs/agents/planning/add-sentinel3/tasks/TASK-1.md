# TASK-1: Add Sentinel-3 STAC Constants

## Goal

Implement Planetary Computer STAC constants for Sentinel-3 OLCI (Collections, Bands, Properties).

## Context & References

- **Source Plan**: `docs/agents/planning/add-sentinel3/add-sentinel3-plan.md`
- **Relevant Specs**: `docs/agents/planning/add-sentinel3/add-sentinel3-spec.md`
- **Existing Code**: `src/geospatial_tools/stac/planetary_computer/constants.py`, `tests/test_planetary_computer_constants.py`

## Subtasks

1. [ ] Add `PlanetaryComputerS3Collection` with `OLCI_L1B` and `OLCI_WFR`.
2. [ ] Add `PlanetaryComputerS3Property` with `ORBIT_STATE`.
3. [ ] Add `PlanetaryComputerS3Band` with `OA16` through `OA21` mapping to `oaXX-radiance` values, and `NIR_865`, `WATER_VAPOUR` aliases.
4. [ ] Write unit tests in `tests/test_planetary_computer_constants.py` to verify values and aliases.

## Requirements & Constraints

- Must inherit from `StrEnum` (Python 3.11+).
- Band keys must exactly match Planetary Computer API asset keys.

## Acceptance Criteria (AC)

- [ ] AC 1: `PlanetaryComputerS3Collection.OLCI_WFR` equals `"sentinel-3-olci-wfr-l2-netcdf"`.
- [ ] AC 2: `PlanetaryComputerS3Band.OA17` equals `"oa17-radiance"`.
- [ ] AC 3: `PlanetaryComputerS3Band.NIR_865` alias correctly resolves to `OA17`'s value.
- [ ] AC 4: All tests pass.

## Testing & Validation

- **Command**: `make test` and `make mypy`
- **Success State**: Zero failures, zero type errors.
- **Manual Verification**: Run `make pylint` to ensure no linting regressions.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: add sentinel-3 stac constants"`
6. [ ] Update this document: Mark as COMPLETE.
