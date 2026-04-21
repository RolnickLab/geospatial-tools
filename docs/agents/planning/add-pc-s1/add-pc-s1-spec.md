# SPEC: Planetary Computer Sentinel-1 GRD Support

## 1. Overview

- **Goal**: Add a `StacSearch`-wrapper class for Sentinel-1 (S1) GRD that builds a SAR query via a builder pattern, executes the search, and downloads assets.
- **Problem Statement**: PC STAC client missing S1 GRD. SAR ignores clouds; it requires polarization / instrument-mode / orbit-state filtering, and has a strict uppercase-property vs. lowercase-asset-key split.
- **Design intent (scope lock)**: A thin, synchronous utility wrapper. Employs a builder pattern for querying (e.g., `.filter_by_instrument_mode()`) allowing fluent and programmatically defined search parameters. The STAC query is derived dynamically from the instance's state rather than an opaque query builder function. **Does not** replicate `BestProductsForFeatures`' tile-coverage workflow, multi-date-range iteration, or standalone module-level search functions.

## 2. Requirements

### Functional Requirements

- [x] Add `PlanetaryComputerS1Collection` (`sentinel-1-grd`) to `constants.py`.
- [x] Add `PlanetaryComputerS1Property` (`sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`) to `constants.py`.
- [x] Add `PlanetaryComputerS1Band` (`vv`, `vh` — lowercase) to `constants.py`.
- [x] Add `PlanetaryComputerS1InstrumentMode` (`IW`, `EW`, `SM`, `WV`) to `constants.py`.
- [x] Add `PlanetaryComputerS1Polarization` (`VV`, `VH`, `HH`, `HV` — uppercase) to `constants.py`.
- [x] Add `PlanetaryComputerS1OrbitState` (`ascending`, `descending` — lowercase) to `constants.py`.
- [x] Create `AbstractSentinel1` in `sentinel_1.py`. Cannot be instantiated directly.
- [x] `AbstractSentinel1.__init__` stores spatial kwargs (`bbox`, `intersects`) + a single pystac-native `date_range: DateLike` as instance attributes. Initializes SAR properties (`instrument_modes`, `polarizations`, `orbit_states`) to `None` and `custom_query_params` to `{}`. Instantiates an internal `StacSearch(PLANETARY_COMPUTER)` as `self.client`.
- [x] `AbstractSentinel1` exposes builder methods that return `self` to allow chaining:
    - `filter_by_instrument_mode(modes: list[PlanetaryComputerS1InstrumentMode] | PlanetaryComputerS1InstrumentMode)`
    - `filter_by_polarization(polarizations: list[PlanetaryComputerS1Polarization] | PlanetaryComputerS1Polarization)`
    - `filter_by_orbit_state(states: list[PlanetaryComputerS1OrbitState] | PlanetaryComputerS1OrbitState)`
    - `with_custom_query(query_params: dict[str, Any])`
- [x] `AbstractSentinel1` exposes `search_results: list[pystac.Item] | None` and `downloaded_assets: list[Asset] | None` state attributes, initialized to `None`.
- [x] Create `Sentinel1Search(AbstractSentinel1)` implementing `search()`, and `download()`.
- [x] `Sentinel1Search.search()` dynamically constructs the STAC `query` dictionary based on the current instance state (`instrument_modes`, `polarizations`, `orbit_states`, `custom_query_params`). Calls `self.client.search(...)` with the built query and stored kwargs, stores the result on `self.search_results`, and returns it.
- [x] `Sentinel1Search.download(bands, base_directory)` calls `self.client.download_search_results(...)`; triggers `self.search()` first if `search_results is None`; stores the result on `self.downloaded_assets`.

### Non-Functional Requirements

- **Consistency**: Domain logic is SAR-specific but uses a fluent builder pattern.
- **Type Safety**: `StrEnum` for all domain constants. No magic strings. Spatial kwargs typed as `geotools_types.BBoxLike` / `geotools_types.IntersectsLike` to match `StacSearch.search()`.
- **Simplicity**: One class, fluent builder methods, `search()`, and `download()`. No module-level search functions. No multi-range loops.

## 3. Technical Constraints & Assumptions

- **Architecture Decision**: `Sentinel1Search` *is* the wrapper. All STAC interaction lives on the class (composition: `self.client = StacSearch(PLANETARY_COMPUTER)`). The STAC query is represented by the class instance's state and is only serialized into a STAC query dictionary at the moment `search()` is called.
- **Builder Pattern**: Replaces a single `build_query` function. This allows users to chain methods like `.filter_by_polarization([...]).filter_by_orbit_state(...)`. It also accommodates multiple properties at once (e.g., searching for both 'ascending' and 'descending' orbit states). `with_custom_query` provides a fallback for uncovered properties.
- **Date Range**: Single `date_range: DateLike` field, delegated unmodified to `StacSearch.search()`. pystac accepts either a single datetime or a `"start/end"` string — that covers the common case.
- **`sar:polarizations` Query Operator**: `sar:polarizations` is a list property in the STAC item. The builder method accepts a list. The `search()` method translates this into the appropriate STAC query syntax. If the STAC query extension is limited (e.g., only supporting a single `contains`), `search()` will apply the first polarization and document that post-filtering might be required.
- **Casing Invariant**: STAC property values for `sar:polarizations` are uppercase (`VV`, `VH`). PC asset keys are lowercase (`vv`, `vh`). These are distinct enums (`PlanetaryComputerS1Polarization` vs. `PlanetaryComputerS1Band`) and must never be conflated. Captured in `KNOWLEDGE.md`.
- **`sar:product_type`**: Out of scope. GRDH / GRDM / GRDF variants documented in `KNOWLEDGE.md` but not filtered.
- **Single-pol items**: Some GRD products lack `vh`. `Sentinel1Search.download()` delegates to `StacSearch.download_search_results()` → `_download_assets()`, which already skips absent asset keys with a log line. No extra handling needed.

## 4. Acceptance Criteria

- [x] SAR constants in `constants.py` are correct (case-distinct `vv`/`vh` vs `VV`/`VH`; three value enums present).
- [x] `sentinel_1.py` exists with `AbstractSentinel1` and `Sentinel1Search`.
- [x] `AbstractSentinel1` stores `bbox`, `intersects`, `date_range`, `collection`, `instrument_modes`, `polarizations`, `orbit_states`, `custom_query_params`, `self.client`, `self.search_results`, `self.downloaded_assets`.
- [x] Builder methods (`filter_by_*` and `with_custom_query`) correctly update instance state and return `self`.
- [x] `Sentinel1Search.search()` dynamically constructs the query dict from the instance's state (using `in` for multiple values where appropriate, and merging with `custom_query_params`), calls `self.client.search(...)`, and stores `self.search_results`.
- [x] `Sentinel1Search.download(bands, base_directory)` calls `self.client.download_search_results(...)`, triggers `search()` if needed, and stores `self.downloaded_assets`.
- [x] Unit and integration tests pass.

## 5. Dependencies

- Planetary Computer STAC API.
- `geospatial_tools.stac.core.StacSearch`, `Asset`, `PLANETARY_COMPUTER`.
- `geospatial_tools.geotools_types.BBoxLike`, `IntersectsLike`, `DateLike`.

## 6. Out of Scope

- `sar:product_type` sub-variants (GRDH/GRDM/GRDF).
- Sentinel-1 RTC collection (`sentinel-1-rtc`).
- SLC data.
- S1 on Copernicus catalog.
- Multi-date-range iteration (callers loop externally if needed).
- Any tile-coverage / best-product selection workflow.
- Post-download raster merging / reprojection orchestration (already available via `Asset` methods; not wrapped here).

## 7. Verification Plan

- **Unit Testing** (in `tests/test_planetary_computer_sentinel1.py`):
    - `AbstractSentinel1` direct instantiation is prevented.
    - Builder methods (`filter_by_instrument_mode`, `filter_by_polarization`, `filter_by_orbit_state`, `with_custom_query`) correctly update instance state and return `self`.
    - `Sentinel1Search.search()` correctly translates instance state into a STAC query dict:
        - Lists of values generate `in` operators (for scalar properties) or appropriate `contains` operators.
        - Merges with `custom_query_params`.
    - `Sentinel1Search.search()` calls `self.client.search` with the built query and stored spatial/date kwargs (mock `StacSearch`). `self.search_results` is populated.
    - `Sentinel1Search.download(bands, base_directory)` triggers `search()` when `search_results is None`; when already populated, calls `download_search_results` directly (mock `StacSearch`). `self.downloaded_assets` is populated.
- **Integration Testing**:
    - `@pytest.mark.integration` marker; skippable via `pytest -m "not integration"`.
    - Instantiate `Sentinel1Search` with pinned `bbox=(-74.0, 45.4, -73.5, 45.7)` (Montreal), pinned `date_range="2023-01-01/2023-01-31"`.
    - Chain builder methods: `.filter_by_instrument_mode(PlanetaryComputerS1InstrumentMode.IW).filter_by_polarization([PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH])`.
    - Call `.search()`; assert results non-empty and every item has `properties["sar:instrument_mode"] == "IW"` and `"VV"` in `properties["sar:polarizations"]`.
