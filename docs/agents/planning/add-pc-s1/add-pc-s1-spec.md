# SPEC: Planetary Computer Sentinel-1 GRD Support

## 1. Overview

- **Goal**: Add Sentinel-1 (S1) GRD STAC client for Planetary Computer.
- **Problem Statement**: PC STAC client is missing S1 GRD support. Sentinel-1 is SAR (active
    microwave), meaning it penetrates clouds. Cloud-cover and optical-nodata semantics do not apply.
    Filtering dimensions are polarization, instrument mode, and orbit state — not cloud cover.
    Optical S2 abstractions must not be copied.

## 2. Requirements

### Functional Requirements

- [ ] Add `PlanetaryComputerS1Collection` (`sentinel-1-grd`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Property` (`sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Band` (`vv`, `vh` — lowercase) to `constants.py`. These are PC asset keys.
- [ ] Add `PlanetaryComputerS1InstrumentMode` (`IW`, `EW`, `SM`, `WV`) to `constants.py`. These are STAC property values (uppercase).
- [ ] Add `PlanetaryComputerS1Polarization` (`VV`, `VH`, `HH`, `HV`) to `constants.py`. These are STAC property values (uppercase). **Distinct from `PlanetaryComputerS1Band` — different case, different use.**
- [ ] Add `PlanetaryComputerS1OrbitState` (`ascending`, `descending`) to `constants.py`. Lowercase per STAC `sat` extension spec.
- [ ] Create `AbstractSentinel1` in `sentinel_1.py`. Requires SAR kwargs (`instrument_mode`, `polarizations`, `orbit_state`, `bbox`, `intersects`). **NO CLOUD COVER. NO OPTICAL FIELDS.**
- [ ] Add `@abstractmethod build_query(self) -> dict` to `AbstractSentinel1` to enforce non-instantiability.
- [ ] Create `Sentinel1Search` extending `AbstractSentinel1`. State bag only — mirrors `Sentinel2Search`.
- [ ] Create standalone function `sentinel_1_search(...)` that uses `StacSearch` directly — mirrors `sentinel_2_complete_tile_search`.

### Non-Functional Requirements

- **Consistency**: Base initialization pattern mirrors S2, but domain logic MUST be SAR-specific.
- **Type Safety**: `StrEnum` for all constants. No magic strings. Typed function signatures using the new value enums.
- **No optical fields**: `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`, `error_results` must NOT appear in `AbstractSentinel1` or `Sentinel1Search`.

## 3. Technical Constraints & Assumptions

### Architecture Decision

- **`Sentinel1Search` is a state bag.** It stores SAR search parameters and implements `build_query()`. It does not call `StacSearch` directly.
- **`sentinel_1_search()` is the standalone STAC function.** It instantiates `Sentinel1Search`, calls `build_query()`, and passes the result to `StacSearch.search_for_date_ranges()`. This mirrors the `sentinel_2_complete_tile_search` pattern in `sentinel_2.py`.

### STAC Query Constraints

- **`sar:polarizations` uses `contains`, not `eq`.** The property is stored as a list in STAC
    (e.g., `["VV", "VH"]`). Using `eq` matches the whole list and will fail for partial matches.
    Use `contains` per polarization:
    ```python
    {"sar:polarizations": {"contains": "VV"}}
    ```
- **Default `instrument_mode` must use the enum, not a raw string.** Use
    `PlanetaryComputerS1InstrumentMode.IW`, not `"IW"`.
- **`orbit_state=None` means no filter.** When `None`, omit `sat:orbit_state` from the query dict entirely.

### Invariant: Asset Keys vs. Property Values

`PlanetaryComputerS1Band` and `PlanetaryComputerS1Polarization` cover the same polarization
concepts but are **different enums for different purposes**:

| Enum                                 | Value              | Use                                           |
| ------------------------------------ | ------------------ | --------------------------------------------- |
| `PlanetaryComputerS1Band.VV`         | `"vv"` (lowercase) | `item.assets["vv"]` — PC asset key            |
| `PlanetaryComputerS1Polarization.VV` | `"VV"` (uppercase) | STAC query `sar:polarizations` property value |

Using the wrong one silently returns empty results or missing assets.

### Spatial Filtering

- `AbstractSentinel1.__init__` accepts `bbox: tuple[float, float, float, float] | None` and
    `intersects: dict | None` kwargs.
- Both are stored as instance attributes and passed through to `StacSearch.search_for_date_ranges()`
    by `sentinel_1_search()`.

### Single-Pol Handling

- Some S1 products are single-pol (VV only). `build_query()` must not crash when
    `polarizations=["VV"]`.
- At download time, missing asset keys are logged at `WARNING` level and skipped — same pattern
    as `core._download_assets`.

### Known Variants (Not Filtered)

- `sar:product_type` exposes sub-variants: GRDH, GRDM, GRDF. Filtering on this field is out of
    scope. Collection `sentinel-1-grd` with `instrument_mode=IW` is sufficient for standard use.

### Existing Systems

- Use `geospatial_tools.stac.core.StacSearch` for all STAC API calls.
- `PLANETARY_COMPUTER` constant from `geospatial_tools.stac.core`.

## 4. Acceptance Criteria

- [ ] All six S1 enum types exist in `constants.py` with correct values (see §2).
- [ ] `PlanetaryComputerS1Band.VV == "vv"` and `PlanetaryComputerS1Polarization.VV == "VV"` — they are not equal.
- [ ] `sentinel_1.py` exists with `AbstractSentinel1` and `Sentinel1Search`.
- [ ] `AbstractSentinel1.__abstractmethods__ == frozenset({'build_query'})` — direct instantiation raises `TypeError`.
- [ ] `AbstractSentinel1` has no `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`, or `error_results` attributes.
- [ ] `AbstractSentinel1.__init__` accepts `bbox` and `intersects` kwargs and stores them as instance attributes.
- [ ] `Sentinel1Search.build_query()` uses `contains` operator for `sar:polarizations` per polarization.
- [ ] `Sentinel1Search.build_query()` omits `sat:orbit_state` from query when `orbit_state=None`.
- [ ] `sentinel_1_search()` exists and calls `StacSearch.search_for_date_ranges()` with the query from `build_query()`.
- [ ] Unit and integration tests pass.

## 5. Dependencies

- Planetary Computer STAC API.
- `geospatial_tools.stac.core.StacSearch`.

## 6. Out of Scope

- Sentinel-1 SLC data.
- Sentinel-1 RTC collection (`sentinel-1-rtc`) — separate PC collection, different product type.
- S1 on Copernicus catalog.
- S1 data downloading / processing (STAC search only).
- Filtering on `sar:product_type` sub-variants (GRDH / GRDM / GRDF).
- Multi-scene mosaicking or tile-coverage workflows (S2-specific concern).

## 7. Verification Plan

### Unit Testing

- Test all six S1 `StrEnum` constants in `tests/test_planetary_computer_constants.py`:
    - Include: `assert PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV`.
- Test `AbstractSentinel1` ABC enforcement in `tests/test_planetary_computer_sentinel1.py`:
    - `pytest.raises(TypeError)` on direct instantiation.
    - Subclass with `build_query()` initializes correctly with all SAR kwargs.
- Test `Sentinel1Search.build_query()`:
    - Returns `contains` operator for each polarization.
    - Omits `sat:orbit_state` when `orbit_state=None`.
    - Single-pol (`polarizations=["VV"]`) does not raise.
- Test `sentinel_1_search()` with mocked `StacSearch`: verify correct query dict is passed.

### Integration Testing

- Marker: `@pytest.mark.integration` — skip in CI with `pytest -m "not integration"`.
- AOI: `bbox=[-122.5, 47.5, -122.0, 48.0]` (Seattle region; dense S1 IW coverage).
- Date range: `["2023-01-01/2023-01-31"]`.
- Assertions: returned items non-empty; each item has `properties["sar:instrument_mode"] == "IW"`.
