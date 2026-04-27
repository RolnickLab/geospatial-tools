# TASK-2: Implement AbstractSentinel1 Base Class

## Goal

Create `AbstractSentinel1` in `sentinel_1.py` as an ABC that provides a fluent builder pattern for SAR search parameters, stores spatial and date filters, owns a `StacSearch` client, and declares abstract methods for execution.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — structural reference only. Do NOT copy optical domain logic.
    - `src/geospatial_tools/stac/core.py` — `StacSearch`, `PLANETARY_COMPUTER`, `Asset`.
    - `src/geospatial_tools/geotools_types.py` — `BBoxLike`, `IntersectsLike`, `DateLike`.

## Subtasks

1. [x] Create new file `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.
2. [x] Implement `AbstractSentinel1` class (inherits `abc.ABC`).
3. [x] Implement typed `__init__` signature with only collection, date, spatial kwargs, and logger:
    ```python
    def __init__(
        self,
        collection: PlanetaryComputerS1Collection | str = PlanetaryComputerS1Collection.GRD,
        date_range: DateLike = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None: ...
    ```
4. [x] Instantiate `self.client: StacSearch = StacSearch(PLANETARY_COMPUTER)` in `__init__`.
5. [x] Initialize SAR properties and results state in `__init__`:
    - `self.instrument_modes: list[PlanetaryComputerS1InstrumentMode] | None = None`
    - `self.polarizations: list[PlanetaryComputerS1Polarization] | None = None`
    - `self.orbit_states: list[PlanetaryComputerS1OrbitState] | None = None`
    - `self.custom_query_params: dict[str, Any] = {}`
    - `self.search_results: list[pystac.Item] | None = None`
    - `self.downloaded_assets: list[Asset] | None = None`
6. [x] Implement fluent builder methods that update state and `return self`:
    - `filter_by_instrument_mode(self, modes: list[PlanetaryComputerS1InstrumentMode] | PlanetaryComputerS1InstrumentMode)` (wrap single item in list)
    - `filter_by_polarization(self, polarizations: list[PlanetaryComputerS1Polarization] | PlanetaryComputerS1Polarization)` (wrap single item in list)
    - `filter_by_orbit_state(self, states: list[PlanetaryComputerS1OrbitState] | PlanetaryComputerS1OrbitState)` (wrap single item in list)
    - `with_custom_query(self, query_params: dict[str, Any])` (update dictionary)
7. [x] Declare `@abstractmethod def search(self) -> list[pystac.Item]: ...`.
8. [x] Declare `@abstractmethod def download(self, bands: list[PlanetaryComputerS1Band | str], base_directory: str | Path) -> list[Asset]: ...`.
9. [x] Write failing tests (TDD Red):
    - Direct instantiation of `AbstractSentinel1` raises `TypeError`.
    - Builder methods correctly update instance state (lists/dicts) and return `self`.
10. [x] Implement `AbstractSentinel1` until tests pass (TDD Green).

## Requirements & Constraints

- Must NOT include optical fields: `max_cloud_cover`, `max_no_data_value`.
- Must NOT include the S2 tile-coverage result containers.
- `date_range` is a single `DateLike` (pystac-native). No multi-range support in this class.
- Spatial kwargs use `geotools_types.BBoxLike` / `geotools_types.IntersectsLike`.
- `StacSearch` is owned via composition (`self.client`).

## Acceptance Criteria (AC)

- [x] `AbstractSentinel1.__abstractmethods__` includes `search` and `download`.
- [x] `TypeError` on direct instantiation of `AbstractSentinel1`.
- [x] No optical fields, no tile-coverage state containers.
- [x] All `__init__` kwargs stored as instance attributes.
- [x] `self.client` is a `StacSearch` instance bound to `PLANETARY_COMPUTER`.
- [x] Builder methods (`filter_by_*`, `with_custom_query`) properly format inputs into lists/dicts, update state, and return `self`.
- [x] Results containers initialized to `None`.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py`
- **Success State**: Subclass with trivial method implementations initializes correctly; builder methods work; direct instantiation of ABC fails.

## Completion Protocol

1. [x] All ACs are met.
2. [x] Tests pass without regressions.
3. [x] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [x] Documentation updated (if applicable).
5. [x] Commit work: `git commit -m "feat(stac-pc): implement AbstractSentinel1 base class with builder pattern"`
6. [x] Update this document: Mark as COMPLETE.
