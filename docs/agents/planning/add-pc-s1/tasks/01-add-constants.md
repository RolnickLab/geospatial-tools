# TASK-1: Add Sentinel-1 Constants

## Goal

Add Sentinel-1 SAR-specific constants to the Planetary Computer constants file to ensure type-safe, magic-string-free usage in the STAC client.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**: src/geospatial_tools/stac/planetary_computer/constants.py, tests/test_planetary_computer_constants.py

## Subtasks

1. [ ] Add `PlanetaryComputerS1Collection` `StrEnum` with value `sentinel-1-grd`.
2. [ ] Add `PlanetaryComputerS1Property` `StrEnum` with values `sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`.
3. [ ] Add `PlanetaryComputerS1Band` `StrEnum` with values `vv`, `vh` (must be lowercase).
4. [ ] Write unit tests for all new constants in `tests/test_planetary_computer_constants.py` to ensure their values are correct.

## Requirements & Constraints

- Constants must be implemented as `StrEnum` to match the existing `PlanetaryComputerS2*` structure.
- `vv` and `vh` must be explicitly lowercase, per Planetary Computer STAC spec.
- No optical properties (like cloud cover) should be included.

## Acceptance Criteria (AC)

- [ ] `PlanetaryComputerS1Collection.GRD` (or similar name) evaluates to `"sentinel-1-grd"`.
- [ ] `PlanetaryComputerS1Property.INSTRUMENT_MODE` evaluates to `"sar:instrument_mode"`.
- [ ] `PlanetaryComputerS1Property.POLARIZATIONS` evaluates to `"sar:polarizations"`.
- [ ] `PlanetaryComputerS1Property.ORBIT_STATE` evaluates to `"sat:orbit_state"`.
- [ ] `PlanetaryComputerS1Band.VV` evaluates to `"vv"`.
- [ ] `PlanetaryComputerS1Band.VH` evaluates to `"vh"`.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_constants.py`
- **Success State**: All constants evaluate to exactly the correct strings without failure.
- **Manual Verification**: Review `constants.py` to ensure NO optical/S2 properties accidentally leaked into the S1 enums.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: add sentinel-1 constants for planetary computer"`
6. [ ] Update this document: Mark as COMPLETE.
