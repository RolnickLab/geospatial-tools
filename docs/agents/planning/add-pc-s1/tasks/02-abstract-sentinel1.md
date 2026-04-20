# TASK-2: Implement AbstractSentinel1 Base Class

## Goal

Create `AbstractSentinel1` in `sentinel_1.py` as a true ABC with SAR-typed kwargs, spatial filter support, and one enforced abstract method.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**: src/geospatial_tools/stac/planetary_computer/sentinel_2.py (for architectural inspiration, NOT for optical domain logic)

## Subtasks

1. [ ] Create new file `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.
2. [ ] Implement `AbstractSentinel1` class (using `abc.ABC`).
3. [ ] Implement typed `__init__` signature:
    ```python
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
    ```
4. [ ] Add `@abstractmethod build_query(self) -> dict[str, Any]` — this is the method that makes the ABC non-instantiable.
5. [ ] Write a failing test asserting `AbstractSentinel1()` raises `TypeError` (TDD Red) — verifying the abstract method enforcement.
6. [ ] Write a failing test for a `ConcreteS1(AbstractSentinel1)` subclass that implements `build_query()` and verifies all kwargs are stored (TDD Red).
7. [ ] Implement `AbstractSentinel1` until both tests pass (TDD Green).
8. [ ] Verify `hasattr(AbstractSentinel1, '__abstractmethods__')` is truthy and contains `'build_query'` in a test.

## Requirements & Constraints

- Must NOT include `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`, or `error_results`. S1 has no tile-coverage workflow.
- `polarizations` defaults to `None`, not `['VV','VH']`. Callers must be explicit. Document this in the docstring.

## Acceptance Criteria (AC)

- [ ] `AbstractSentinel1.__abstractmethods__ == frozenset({'build_query'})`.
- [ ] `TypeError` on direct instantiation of `AbstractSentinel1`.
- [ ] Explicit lack of optical fields.
- [ ] `bbox` and `intersects` are stored as instance attributes.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py`
- **Success State**: Subclass initializes correctly, property assignments work, instantiation of the ABC fails.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat(stac-pc): implement AbstractSentinel1"`
6. [ ] Update this document: Mark as COMPLETE.
