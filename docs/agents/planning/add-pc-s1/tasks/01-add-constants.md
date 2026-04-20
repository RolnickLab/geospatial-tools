# TASK-1: Add Sentinel-1 Constants

## Goal

Add all six S1 StrEnum types to `constants.py`, covering collection, query properties, asset band keys, instrument mode values, polarization values, and orbit state values.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**: src/geospatial_tools/stac/planetary_computer/constants.py, tests/test_planetary_computer_constants.py

## Subtasks

1. [ ] Add `PlanetaryComputerS1Collection` `StrEnum` with value `GRD = "sentinel-1-grd"`.
2. [ ] Add `PlanetaryComputerS1Property` `StrEnum` with values `INSTRUMENT_MODE = "sar:instrument_mode"`, `POLARIZATIONS = "sar:polarizations"`, `ORBIT_STATE = "sat:orbit_state"`.
3. [ ] Add `PlanetaryComputerS1Band` `StrEnum` with values `VV = "vv"`, `VH = "vh"`.
4. [ ] Add `PlanetaryComputerS1InstrumentMode` `StrEnum` with values `IW = "IW"`, `EW = "EW"`, `SM = "SM"`, `WV = "WV"`.
5. [ ] Add `PlanetaryComputerS1Polarization` `StrEnum` with values `VV = "VV"`, `VH = "VH"`, `HH = "HH"`, `HV = "HV"`.
6. [ ] Add `PlanetaryComputerS1OrbitState` `StrEnum` with values `ASCENDING = "ascending"`, `DESCENDING = "descending"`.
7. [ ] Write failing tests for `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, `PlanetaryComputerS1OrbitState` in `tests/test_planetary_computer_constants.py` (TDD Red).
8. [ ] Implement the three new enums in `constants.py` until tests pass (TDD Green).
9. [ ] Add explicit test `assert PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV` to verify the lowercase/uppercase invariant.
10. [ ] Export all six new types from `src/geospatial_tools/stac/planetary_computer/__init__.py`.

## Requirements & Constraints

- Constants must be implemented as `StrEnum`.
- Property value enums use uppercase (SAR convention). Asset key enums use lowercase (PC STAC spec). These are distinct and must not be substituted.

## Acceptance Criteria (AC)

- [ ] `PlanetaryComputerS1Collection` has correct value.
- [ ] `PlanetaryComputerS1Property` has correct values.
- [ ] `PlanetaryComputerS1Band` has correct values.
- [ ] `PlanetaryComputerS1InstrumentMode` has correct values.
- [ ] `PlanetaryComputerS1Polarization` has correct values.
- [ ] `PlanetaryComputerS1OrbitState` has correct values.
- [ ] `assert PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV` passes.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_constants.py`
- **Success State**: All constants evaluate correctly.
- **Manual Verification**: Review `constants.py`.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat(stac-pc): add S1 constants"`
6. [ ] Update this document: Mark as COMPLETE.
