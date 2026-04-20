# TASK-1: Add Sentinel-1 Constants

## 1. Goal

Add all six S1 `StrEnum` types to `constants.py`, covering collection identifier, query property
keys, asset band keys, instrument mode values, polarization values, and orbit state values.
Export all six from `__init__.py`. Every downstream S1 task depends on these types being present
and correct.

## 2. Context & References

- **Source Plan**: `docs/agents/planning/add-pc-s1/add-pc-s1.md`

- **Relevant Specs**: `docs/agents/planning/add-pc-s1/add-pc-s1-spec.md`

- **Key files**:

    - `src/geospatial_tools/stac/planetary_computer/constants.py` — append the six new enums here
    - `src/geospatial_tools/stac/planetary_computer/__init__.py` — export all six new types
    - `tests/test_planetary_computer_constants.py` — extend with S1 test classes

- **Relevant skills**: `python`, `tdd`

- **Interface contract (complete, inline):**

    ```python
    class PlanetaryComputerS1Collection(StrEnum):
        """Planetary Computer Sentinel-1 Collections."""
        GRD = "sentinel-1-grd"

    class PlanetaryComputerS1Property(StrEnum):
        """Planetary Computer Sentinel-1 STAC query property keys."""
        INSTRUMENT_MODE = "sar:instrument_mode"
        POLARIZATIONS   = "sar:polarizations"
        ORBIT_STATE     = "sat:orbit_state"

    class PlanetaryComputerS1Band(StrEnum):
        """PC asset keys for S1 GRD bands — lowercase per PC STAC spec."""
        VV = "vv"
        VH = "vh"

    class PlanetaryComputerS1InstrumentMode(StrEnum):
        """SAR instrument mode property values — uppercase per SAR convention."""
        IW = "IW"
        EW = "EW"
        SM = "SM"
        WV = "WV"

    class PlanetaryComputerS1Polarization(StrEnum):
        """sar:polarizations property values — uppercase per SAR convention."""
        VV = "VV"
        VH = "VH"
        HH = "HH"
        HV = "HV"

    class PlanetaryComputerS1OrbitState(StrEnum):
        """sat:orbit_state property values — lowercase per STAC sat extension."""
        ASCENDING  = "ascending"
        DESCENDING = "descending"
    ```

    **Invariant:** `PlanetaryComputerS1Band.VV == "vv"` (lowercase — used as `item.assets["vv"]`).
    `PlanetaryComputerS1Polarization.VV == "VV"` (uppercase — used in STAC query property values).
    These serve different purposes and must never be substituted for each other.

## 3. Subtasks

- [ ] 1. Write failing tests for `PlanetaryComputerS1Collection`, `PlanetaryComputerS1Property`,
    and `PlanetaryComputerS1Band` in `tests/test_planetary_computer_constants.py` (TDD Red).
- [ ] 2. Write failing tests for `PlanetaryComputerS1InstrumentMode`,
    `PlanetaryComputerS1Polarization`, and `PlanetaryComputerS1OrbitState` (TDD Red).
- [ ] 3. Add invariant test:
    `assert PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV` (TDD Red).
- [ ] 4. Implement all six enums in `constants.py` exactly as shown in the interface contract above
    until all tests pass (TDD Green).
- [ ] 5. Export all six new types from
    `src/geospatial_tools/stac/planetary_computer/__init__.py`.
- [ ] 6. Run `ruff check` and `mypy` — fix any issues (TDD Refactor).

## 4. Requirements & Constraints

- **Technical:** All six enums must be `StrEnum`. Follow the docstring style of existing
    `PlanetaryComputerS2*` classes.
- **Invariant:** Property value enums use uppercase (SAR convention for instrument mode and
    polarization). Asset key enums use lowercase (PC STAC spec). These are distinct and must not
    be substituted for each other.
- **No optical fields:** No `cloud_cover`, `eo:cloud_cover`, or any S2-specific property must
    appear in any S1 enum.
- **Out of scope:** `AbstractSentinel1`, `Sentinel1Search`, `sentinel_1_search()` — those are
    TASK-2 and TASK-3. `KNOWLEDGE.md` update — that is a separate task.

## 5. Acceptance Criteria

- [ ] AC-1: `PlanetaryComputerS1Collection.GRD == "sentinel-1-grd"`.
- [ ] AC-2: `PlanetaryComputerS1Property.INSTRUMENT_MODE == "sar:instrument_mode"`.
- [ ] AC-3: `PlanetaryComputerS1Property.POLARIZATIONS == "sar:polarizations"`.
- [ ] AC-4: `PlanetaryComputerS1Property.ORBIT_STATE == "sat:orbit_state"`.
- [ ] AC-5: `PlanetaryComputerS1Band.VV == "vv"` and `PlanetaryComputerS1Band.VH == "vh"`.
- [ ] AC-6: `PlanetaryComputerS1InstrumentMode.IW == "IW"`, `.EW == "EW"`, `.SM == "SM"`, `.WV == "WV"`.
- [ ] AC-7: `PlanetaryComputerS1Polarization.VV == "VV"`, `.VH == "VH"`, `.HH == "HH"`, `.HV == "HV"`.
- [ ] AC-8: `PlanetaryComputerS1OrbitState.ASCENDING == "ascending"`, `.DESCENDING == "descending"`.
- [ ] AC-9: `PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV` (invariant test passes).
- [ ] AC-10: All six types importable from `geospatial_tools.stac.planetary_computer`.
- [ ] AC-11: All new code passes `ruff check` and `mypy` with zero errors.
- [ ] AC-12: `pytest tests/test_planetary_computer_constants.py -x` passes with no regressions.

## 6. Testing & Validation

```bash
# Run targeted tests
pytest tests/test_planetary_computer_constants.py -v

# Type-check
mypy src/geospatial_tools/stac/planetary_computer/constants.py

# Lint
ruff check src/geospatial_tools/stac/planetary_computer/constants.py

# Verify exports
python -c "from geospatial_tools.stac.planetary_computer import (
    PlanetaryComputerS1Collection, PlanetaryComputerS1Property, PlanetaryComputerS1Band,
    PlanetaryComputerS1InstrumentMode, PlanetaryComputerS1Polarization, PlanetaryComputerS1OrbitState
); print('all imports ok')"

# Verify invariant
python -c "
from geospatial_tools.stac.planetary_computer import PlanetaryComputerS1Band, PlanetaryComputerS1Polarization
assert PlanetaryComputerS1Band.VV == 'vv'
assert PlanetaryComputerS1Polarization.VV == 'VV'
assert PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV
print('invariant ok')
"
```

Expected: all commands exit 0; `pytest` shows all S1 constant tests passing.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm expected output.
3. Stage and commit:
    ```bash
    git add src/geospatial_tools/stac/planetary_computer/constants.py \
            src/geospatial_tools/stac/planetary_computer/__init__.py \
            tests/test_planetary_computer_constants.py
    git commit -m "feat(stac-pc): add S1 constants for planetary computer — closes TASK-1"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-2.
