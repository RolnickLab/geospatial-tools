# SPEC: Planetary Computer Sentinel-1 GRD Support

## 1. Overview

- **Goal**: Add a `StacSearch`-wrapper class for Sentinel-1 (S1) GRD that builds a SAR query, executes the search, and downloads assets.
- **Problem Statement**: PC STAC client missing S1 GRD. SAR ignores clouds; it requires polarization / instrument-mode / orbit-state filtering, and has a strict uppercase-property vs. lowercase-asset-key split.
- **Design intent (scope lock)**: A thin, synchronous utility wrapper. Mirrors the *structure* of `AbstractSentinel2` / `Sentinel2Search` (abstract base + concrete subclass, kwargs stored as state), but **does not** replicate `BestProductsForFeatures`' tile-coverage workflow, multi-date-range iteration, or standalone module-level search functions. Callers who need multi-range behavior can loop externally.

## 2. Requirements

### Functional Requirements

- [x] Add `PlanetaryComputerS1Collection` (`sentinel-1-grd`) to `constants.py`.
- [x] Add `PlanetaryComputerS1Property` (`sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`) to `constants.py`.
- [x] Add `PlanetaryComputerS1Band` (`vv`, `vh` — lowercase) to `constants.py`.
- [x] Add `PlanetaryComputerS1InstrumentMode` (`IW`, `EW`, `SM`, `WV`) to `constants.py`.
- [x] Add `PlanetaryComputerS1Polarization` (`VV`, `VH`, `HH`, `HV` — uppercase) to `constants.py`.
- [x] Add `PlanetaryComputerS1OrbitState` (`ascending`, `descending` — lowercase) to `constants.py`.
- [ ] Create `AbstractSentinel1` in `sentinel_1.py`. Cannot be instantiated directly (requires at least one `@abstractmethod`).
- [ ] `AbstractSentinel1.__init__` stores SAR kwargs + spatial kwargs (`bbox`, `intersects`) + a single pystac-native `date_range: DateLike` as instance attributes. Instantiates an internal `StacSearch(PLANETARY_COMPUTER)` as `self.client`.
- [ ] `AbstractSentinel1` exposes `search_results: list[pystac.Item] | None` and `downloaded_assets: list[Asset] | None` state attributes, initialized to `None`.
- [ ] `AbstractSentinel1` declares `@abstractmethod build_query(self) -> dict[str, Any]`.
- [ ] Create `Sentinel1Search(AbstractSentinel1)` implementing `build_query()`, `search()`, and `download()`.
- [ ] `Sentinel1Search.search()` calls `self.client.search(...)` with the built query and stored kwargs, stores the result on `self.search_results`, and returns it.
- [ ] `Sentinel1Search.download(bands, base_directory)` calls `self.client.download_search_results(...)`; triggers `self.search()` first if `search_results is None`; stores the result on `self.downloaded_assets`.

### Non-Functional Requirements

- **Consistency**: Structure mirrors `AbstractSentinel2` / `Sentinel2Search` (ABC + concrete subclass); domain logic is SAR-specific.
- **Type Safety**: `StrEnum` for all domain constants. No magic strings. Spatial kwargs typed as `geotools_types.BBoxLike` / `geotools_types.IntersectsLike` to match `StacSearch.search()`.
- **Simplicity**: One class, three methods (`build_query`, `search`, `download`). No module-level search functions. No multi-range loops.

## 3. Technical Constraints & Assumptions

- **Architecture Decision**: `Sentinel1Search` *is* the wrapper. All STAC interaction lives on the class (composition: `self.client = StacSearch(PLANETARY_COMPUTER)`). No standalone `sentinel_1_search(...)` function.
- **Date Range**: Single `date_range: DateLike` field, delegated unmodified to `StacSearch.search()`. pystac accepts either a single datetime or a `"start/end"` string — that covers the common case. If a user needs multiple disjoint ranges, they instantiate the class multiple times or loop externally. This is a deliberate scope lock.
- **`sar:polarizations` Query Operator**: `sar:polarizations` is a list property. The STAC `query` extension supports a single `contains` per property, so `build_query()` emits `{"sar:polarizations": {"contains": "<first-pol>"}}` using `self.polarizations[0]`. If callers need strict "all requested polarizations present" semantics, they post-filter `self.search_results` — this limitation is documented in the `build_query()` docstring. In practice, PC IW items are dual-pol (VV + VH) almost everywhere, so filtering on the first pol is sufficient for the common case.
- **Casing Invariant**: STAC property values for `sar:polarizations` are uppercase (`VV`, `VH`). PC asset keys are lowercase (`vv`, `vh`). These are distinct enums (`PlanetaryComputerS1Polarization` vs. `PlanetaryComputerS1Band`) and must never be conflated. Captured in `KNOWLEDGE.md`.
- **Default Instrument Mode**: `PlanetaryComputerS1InstrumentMode.IW` enum member, not a raw string.
- **`polarizations` default**: `None` (no query-level filter). Callers pass a list explicitly.
- **`sar:product_type`**: Out of scope. GRDH / GRDM / GRDF variants documented in `KNOWLEDGE.md` but not filtered.
- **Single-pol items**: Some GRD products lack `vh`. `Sentinel1Search.download()` delegates to `StacSearch.download_search_results()` → `_download_assets()`, which already skips absent asset keys with a log line. No extra handling needed; the test must confirm this pathway.

## 4. Acceptance Criteria

- [x] SAR constants in `constants.py` are correct (case-distinct `vv`/`vh` vs `VV`/`VH`; three value enums present).
- [ ] `sentinel_1.py` exists with `AbstractSentinel1` (ABC with one `@abstractmethod`) and `Sentinel1Search`.
- [ ] `AbstractSentinel1` has no optical fields (`max_cloud_cover`, `max_no_data_value`, tile-coverage result containers).
- [ ] `AbstractSentinel1` stores `bbox`, `intersects`, `date_range`, `collection`, `instrument_mode`, `polarizations`, `orbit_state`, `self.client` (StacSearch instance), `self.search_results`, `self.downloaded_assets`.
- [ ] `AbstractSentinel1` cannot be instantiated directly.
- [ ] `Sentinel1Search.build_query()` uses `contains` for the first polarization (when provided) and `eq` for `instrument_mode` / `orbit_state`.
- [ ] `Sentinel1Search.search()` calls `self.client.search(...)` with correct kwargs and stores `self.search_results`.
- [ ] `Sentinel1Search.download(bands, base_directory)` calls `self.client.download_search_results(...)`, triggers `search()` if needed, and stores `self.downloaded_assets`.
- [ ] Unit and integration tests pass.

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
    - `AbstractSentinel1()` raises `TypeError` (direct instantiation rejected).
    - `AbstractSentinel1.__abstractmethods__` contains `'build_query'`.
    - `Sentinel1Search.build_query()` emits `contains` for the first polarization, `eq` for `instrument_mode`, omits `orbit_state` when `None`, includes `orbit_state` with `eq` when set.
    - `Sentinel1Search.build_query()` does not crash when `polarizations=None` or `polarizations=["VV"]`.
    - `Sentinel1Search.search()` calls `self.client.search` with the built query and stored spatial/date kwargs (mock `StacSearch`). `self.search_results` is populated.
    - `Sentinel1Search.download(bands, base_directory)` triggers `search()` when `search_results is None`; when already populated, calls `download_search_results` directly (mock `StacSearch`). `self.downloaded_assets` is populated.
- **Integration Testing**:
    - `@pytest.mark.integration` marker; skippable via `pytest -m "not integration"`.
    - Instantiate `Sentinel1Search` with pinned `bbox=(-122.5, 47.5, -122.0, 48.0)` (Seattle), pinned `date_range="2023-01-01/2023-01-31"`, `instrument_mode=PlanetaryComputerS1InstrumentMode.IW`, `polarizations=[PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH]`.
    - Call `.search()`; assert results non-empty and every item has `properties["sar:instrument_mode"] == "IW"` and `"VV"` in `properties["sar:polarizations"]`.
