# TASK-004: Rewrite tasks/02-abstract-sentinel1.md with real @abstractmethod, typed args, and trimmed state

## 1. Goal

Produce a corrected implementation task for `AbstractSentinel1` that (a) adds a real
`@abstractmethod` so the ABC guarantee holds, (b) uses the new value enums for typed
`instrument_mode` and `polarizations`, (c) accepts `bbox`/`intersects` for spatial filtering,
and (d) removes the S2-specific state containers that have no SAR equivalent.

## 2. Context & References

- **Review findings:** Issues 2, 3, 4, 7, 8, 10 in `docs/agents/planning/add-pc-s1/review.md`

- **Upstream tasks:** TASK-003 — interface contract for value enums required here (inline excerpt below).

- **Key files:**

    - `docs/agents/planning/add-pc-s1/tasks/02-abstract-sentinel1.md` — file to replace
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — reference for `AbstractSentinel2` pattern (do NOT copy state containers)
    - `src/geospatial_tools/stac/core.py` — `StacSearch.search()` signature for `bbox`/`intersects` types

- **Relevant skills:** `python`, `systemdesign`, `tdd`

- **Interface contract (inline):**

    ```python
    # From TASK-003 (constants)
    class PlanetaryComputerS1InstrumentMode(StrEnum):
        IW = "IW"   # default

    class PlanetaryComputerS1Polarization(StrEnum):
        VV = "VV"
        VH = "VH"
        HH = "HH"
        HV = "HV"

    class PlanetaryComputerS1OrbitState(StrEnum):
        ASCENDING  = "ascending"
        DESCENDING = "descending"

    # Target AbstractSentinel1 signature
    class AbstractSentinel1(ABC):
        def __init__(
            self,
            collection: PlanetaryComputerS1Collection | str = PlanetaryComputerS1Collection.GRD,
            date_ranges: list[str] | None = None,
            instrument_mode: PlanetaryComputerS1InstrumentMode | str = PlanetaryComputerS1InstrumentMode.IW,
            polarizations: list[PlanetaryComputerS1Polarization] | None = None,
            orbit_state: PlanetaryComputerS1OrbitState | None = None,
            bbox: tuple[float, float, float, float] | None = None,
            intersects: dict | None = None,
            logger: logging.Logger = LOGGER,
        ) -> None: ...

        @abstractmethod
        def build_query(self) -> dict[str, Any]:
            """Build the STAC query dict for this search configuration."""
            ...
    ```

    **Note:** `polarizations` defaults to `None` (not `["VV", "VH"]` — caller must be explicit).
    No `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`,
    or `error_results` on the base class.

## 3. Subtasks

- [ ] 1. Update §Goal: "Create `AbstractSentinel1` in `sentinel_1.py` as a true ABC with SAR-typed kwargs, spatial filter support, and one enforced abstract method."
- [ ] 2. Update §Subtasks to replace `AbstractSentinel2`-mirrored init with the typed signature above.
- [ ] 3. Add subtask: "Add `@abstractmethod build_query(self) -> dict[str, Any]` — this is the method that makes the ABC non-instantiable."
- [ ] 4. Add subtask: "Write a failing test asserting `AbstractSentinel1()` raises `TypeError` (TDD Red) — verifying the abstract method enforcement."
- [ ] 5. Add subtask: "Write a failing test for a `ConcreteS1(AbstractSentinel1)` subclass that implements `build_query()` and verifies all kwargs are stored (TDD Red)."
- [ ] 6. Add subtask: "Implement `AbstractSentinel1` until both tests pass (TDD Green)."
- [ ] 7. Add subtask: "Verify `hasattr(AbstractSentinel1, '__abstractmethods__')` is truthy and contains `'build_query'` in a test."
- [ ] 8. Update §Requirements & Constraints: "Must NOT include `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`, or `error_results`. S1 has no tile-coverage workflow."
- [ ] 9. Update §Requirements & Constraints: "`polarizations` defaults to `None`, not `['VV','VH']`. Callers must be explicit. Document this in the docstring."
- [ ] 10. Update §Acceptance Criteria to include: `@abstractmethod` present, `TypeError` on direct instantiation, no optical/S2 fields, `bbox`/`intersects` accepted and stored.
- [ ] 11. Update commit message to scoped format: `feat(stac-pc): implement AbstractSentinel1`.

## 4. Requirements & Constraints

- **Technical:** Markdown document only — no code changes in this task.
- **Business:** The resulting implementation task must be self-contained. The interface contract above must appear inline in the rewritten `02-abstract-sentinel1.md`.
- **Out of scope:** `Sentinel1Search` concrete class (TASK-005 rewrite handles that). `KNOWLEDGE.md` (TASK-005).

## 5. Acceptance Criteria

- [ ] AC-1: Rewritten `02-abstract-sentinel1.md` includes the full typed `__init__` signature inline.
- [ ] AC-2: Task includes `@abstractmethod build_query()` as a required subtask.
- [ ] AC-3: Task has TDD Red/Green subtasks — failing tests before implementation.
- [ ] AC-4: Task §Requirements states: no optical fields, `polarizations` defaults to `None`.
- [ ] AC-5: Task §AC includes a binary check: `AbstractSentinel1.__abstractmethods__ == frozenset({'build_query'})`.
- [ ] AC-6: Task §AC includes a binary check: `bbox` and `intersects` stored as instance attributes.
- [ ] AC-7: Commit message in §Completion Protocol uses `feat(stac-pc):` scope.

## 6. Testing & Validation

```bash
# Verify mandatory content in the rewritten task
grep -n "abstractmethod\|@abstractmethod" docs/agents/planning/add-pc-s1/tasks/02-abstract-sentinel1.md
grep -n "build_query" docs/agents/planning/add-pc-s1/tasks/02-abstract-sentinel1.md
grep -n "bbox\|intersects" docs/agents/planning/add-pc-s1/tasks/02-abstract-sentinel1.md
grep -n "max_cloud_cover\|successful_results" docs/agents/planning/add-pc-s1/tasks/02-abstract-sentinel1.md
# This last grep should return zero matches (forbidden fields must not appear)
```

Expected: first three greps return ≥1 match; last grep returns 0 matches.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6. Confirm first three greps match; last grep returns empty.
3. Stage and commit:
    ```bash
    git add docs/agents/planning/add-pc-s1/tasks/02-abstract-sentinel1.md
    git commit -m "docs(stac-pc): rewrite task-02 abstract class with @abstractmethod and typed args — closes TASK-004"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-005.
