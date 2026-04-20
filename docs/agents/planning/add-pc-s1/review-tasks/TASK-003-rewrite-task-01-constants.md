# TASK-003: Rewrite tasks/01-add-constants.md with three missing value enums and asset/property invariant

## 1. Goal

Produce a corrected implementation task for S1 constants that includes all six required enums
(not three), documents the uppercase/lowercase invariant in subtasks and ACs, and provides
complete test coverage for both property values and asset keys.

## 2. Context & References

- **Review findings:** Issues 4, 5, 14 in `docs/agents/planning/add-pc-s1/review.md`

- **Upstream tasks:** TASK-001 (spec), TASK-002 (plan) — this task rewrites the implementation guide; it does not execute code.

- **Key files:**

    - `docs/agents/planning/add-pc-s1/tasks/01-add-constants.md` — file to replace
    - `src/geospatial_tools/stac/planetary_computer/constants.py` — existing enums to mirror
    - `tests/test_planetary_computer_constants.py` — existing test file to extend

- **Relevant skills:** `python`, `tdd`

- **Interface contract (inline from spec TASK-001):**

    ```python
    # Property values (STAC query — uppercase)
    class PlanetaryComputerS1Collection(StrEnum):
        GRD = "sentinel-1-grd"

    class PlanetaryComputerS1Property(StrEnum):
        INSTRUMENT_MODE = "sar:instrument_mode"
        POLARIZATIONS   = "sar:polarizations"
        ORBIT_STATE     = "sat:orbit_state"

    class PlanetaryComputerS1Band(StrEnum):  # asset keys — lowercase
        VV = "vv"
        VH = "vh"

    class PlanetaryComputerS1InstrumentMode(StrEnum):  # property values — uppercase
        IW = "IW"
        EW = "EW"
        SM = "SM"
        WV = "WV"

    class PlanetaryComputerS1Polarization(StrEnum):  # property values — uppercase
        VV = "VV"
        VH = "VH"
        HH = "HH"
        HV = "HV"

    class PlanetaryComputerS1OrbitState(StrEnum):  # sat extension — lowercase
        ASCENDING  = "ascending"
        DESCENDING = "descending"
    ```

    **Invariant:** `PlanetaryComputerS1Band.VV == "vv"` (lowercase asset key).
    `PlanetaryComputerS1Polarization.VV == "VV"` (uppercase STAC property value).
    These are different enums for different uses and must never be substituted for each other.

## 3. Subtasks

- [ ] 1. Update §Goal to: "Add all six S1 StrEnum types to `constants.py`, covering collection, query properties, asset band keys, instrument mode values, polarization values, and orbit state values."
- [ ] 2. Update §Subtasks to list all six enums with values as shown in the interface contract above.
- [ ] 3. Add subtask: "Write failing tests for `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, `PlanetaryComputerS1OrbitState` in `tests/test_planetary_computer_constants.py` (TDD Red)."
- [ ] 4. Add subtask: "Implement the three new enums in `constants.py` until tests pass (TDD Green)."
- [ ] 5. Add subtask: "Add explicit test `assert PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV` to verify the lowercase/uppercase invariant."
- [ ] 6. Update §Acceptance Criteria to include ACs for all six enums and the invariant test.
- [ ] 7. Update §Requirements & Constraints to state: "Property value enums use uppercase (SAR convention). Asset key enums use lowercase (PC STAC spec). These are distinct and must not be substituted."
- [ ] 8. Update §Completion Protocol commit message to scoped format: `feat(stac-pc): add S1 constants`.
- [ ] 9. Add subtask: "Export all six new types from `src/geospatial_tools/stac/planetary_computer/__init__.py`."

## 4. Requirements & Constraints

- **Technical:** Markdown document only — no code changes in this task.
- **Business:** The implementation task produced here must be self-contained; an implementer should not need TASK-001 open to understand what to build.
- **Out of scope:** Implementing the constants (that is the job of the rewritten `01-add-constants.md`). `KNOWLEDGE.md` update (TASK-005).

## 5. Acceptance Criteria

- [ ] AC-1: Rewritten `01-add-constants.md` lists all six enum types with correct values inline.
- [ ] AC-2: Task includes TDD Red/Green subtasks for each enum.
- [ ] AC-3: Task has an explicit AC requiring `PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV`.
- [ ] AC-4: Task §Requirements & Constraints documents the uppercase/lowercase invariant.
- [ ] AC-5: Task includes subtask for exporting new types from `__init__.py`.
- [ ] AC-6: Commit message in §Completion Protocol uses `feat(stac-pc):` scope.

## 6. Testing & Validation

```bash
# Verify mandatory content in the rewritten task
grep -n "PlanetaryComputerS1InstrumentMode\|PlanetaryComputerS1Polarization\|PlanetaryComputerS1OrbitState" \
    docs/agents/planning/add-pc-s1/tasks/01-add-constants.md

grep -n "PlanetaryComputerS1Band.VV.*!=.*PlanetaryComputerS1Polarization" \
    docs/agents/planning/add-pc-s1/tasks/01-add-constants.md

grep -n "__init__.py" docs/agents/planning/add-pc-s1/tasks/01-add-constants.md

grep -n "feat(stac-pc)" docs/agents/planning/add-pc-s1/tasks/01-add-constants.md
```

Expected: each grep returns at least one match.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm each grep returns at least one match.
3. Stage and commit:
    ```bash
    git add docs/agents/planning/add-pc-s1/tasks/01-add-constants.md
    git commit -m "docs(stac-pc): rewrite task-01 constants with missing value enums — closes TASK-003"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-004.
