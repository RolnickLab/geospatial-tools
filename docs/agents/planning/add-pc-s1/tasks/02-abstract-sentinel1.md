# TASK-2: Implement AbstractSentinel1 Base Class

## Goal

Create `AbstractSentinel1` in `sentinel_1.py` as a true ABC with SAR-typed kwargs, spatial-filter support, a single pystac-native `date_range`, an owned `StacSearch` client, result-state attributes, and one enforced abstract method.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — structural reference only (ABC + concrete subclass pattern). Do NOT copy optical domain logic (cloud cover, nodata), the tile-coverage workflow, or `successful_results` / `incomplete_results` / `error_results` state.
    - `src/geospatial_tools/stac/core.py` — `StacSearch`, `PLANETARY_COMPUTER`, `Asset`.
    - `src/geospatial_tools/geotools_types.py` — `BBoxLike`, `IntersectsLike`, `DateLike`.

## Subtasks

1. [ ] Create new file `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.
2. [ ] Implement `AbstractSentinel1` class (inherits `abc.ABC`).
3. [ ] Implement typed `__init__` signature:
    ```python
    def __init__(
        self,
        collection: PlanetaryComputerS1Collection | str = PlanetaryComputerS1Collection.GRD,
        date_range: DateLike = None,
        instrument_mode: PlanetaryComputerS1InstrumentMode | str = PlanetaryComputerS1InstrumentMode.IW,
        polarizations: list[PlanetaryComputerS1Polarization] | None = None,
        orbit_state: PlanetaryComputerS1OrbitState | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None: ...
    ```
4. [ ] Instantiate `self.client: StacSearch = StacSearch(PLANETARY_COMPUTER)` in `__init__`.
5. [ ] Initialize state attributes: `self.search_results: list[pystac.Item] | None = None`, `self.downloaded_assets: list[Asset] | None = None`.
6. [ ] Declare `@abstractmethod def build_query(self) -> dict[str, Any]: ...`.
7. [ ] Write a failing test asserting `AbstractSentinel1()` raises `TypeError` (TDD Red).
8. [ ] Write a failing test for a `ConcreteS1(AbstractSentinel1)` subclass that implements a trivial `build_query() -> dict` and verifies every `__init__` kwarg is stored as an instance attribute with the correct value, and that `self.client` is a `StacSearch` instance with `catalog_name == PLANETARY_COMPUTER` (TDD Red).
9. [ ] Write a failing test asserting `AbstractSentinel1.__abstractmethods__ == frozenset({'build_query'})` (TDD Red).
10. [ ] Implement `AbstractSentinel1` until all three tests pass (TDD Green).
11. [ ] Add a docstring note on `polarizations`: "Defaults to `None` (no query-level filter). Only `polarizations[0]` is used at query time — see `Sentinel1Search.build_query()`."

## Requirements & Constraints

- Must NOT include optical fields: `max_cloud_cover`, `max_no_data_value`.
- Must NOT include the S2 tile-coverage result containers: `successful_results`, `incomplete_results`, `error_results`.
- `polarizations` defaults to `None`, not `['VV','VH']`. Callers must be explicit.
- `date_range` is a single `DateLike` (pystac-native). No multi-range support in this class.
- Spatial kwargs use `geotools_types.BBoxLike` / `geotools_types.IntersectsLike` to match `StacSearch.search()` exactly.
- `StacSearch` is owned via composition (`self.client`); do NOT subclass `StacSearch`.

## Acceptance Criteria (AC)

- [ ] `AbstractSentinel1.__abstractmethods__ == frozenset({'build_query'})`.
- [ ] `TypeError` on direct instantiation of `AbstractSentinel1`.
- [ ] No optical fields, no tile-coverage state containers.
- [ ] All `__init__` kwargs (`collection`, `date_range`, `instrument_mode`, `polarizations`, `orbit_state`, `bbox`, `intersects`, `logger`) stored as instance attributes.
- [ ] `self.client` is a `StacSearch` instance bound to `PLANETARY_COMPUTER`.
- [ ] `self.search_results` and `self.downloaded_assets` initialized to `None`.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py`
- **Success State**: Subclass initializes correctly; all attributes present and typed; direct instantiation of the ABC fails with `TypeError`.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat(stac-pc): implement AbstractSentinel1 base class"`
6. [ ] Update this document: Mark as COMPLETE.
