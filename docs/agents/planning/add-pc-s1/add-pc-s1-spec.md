# SPEC: Planetary Computer Sentinel-1 GRD Support

## 1. Overview

- **Goal**: Add Sentinel-1 (S1) GRD STAC client with full SAR query semantics.
- **Problem Statement**: PC STAC client missing S1 GRD. SAR ignores clouds, requires specific polarization, instrument mode, and orbit state filtering, as well as strict handling of uppercase STAC properties vs lowercase asset keys.

## 2. Requirements

### Functional Requirements

- [ ] Add `PlanetaryComputerS1Collection` (`sentinel-1-grd`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Property` (`sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Band` (`vv`, `vh` - lowercase) to `constants.py`.
- [ ] Add `PlanetaryComputerS1InstrumentMode` (`IW`, `EW`, `SM`, `WV`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Polarization` (`VV`, `VH`, `HH`, `HV` - uppercase) to `constants.py`.
- [ ] Add `PlanetaryComputerS1OrbitState` (`ascending`, `descending` - lowercase) to `constants.py`.
- [ ] Create `AbstractSentinel1` in `sentinel_1.py`. Cannot be instantiated directly (requires at least one `@abstractmethod`).
- [ ] `AbstractSentinel1.__init__` accepts `bbox` and `intersects` kwargs; both are passed through to `StacSearch.search()`.
- [ ] Create `Sentinel1Search` extending `AbstractSentinel1` as a state bag.

### Non-Functional Requirements

- **Consistency**: Base structure mimics S2, but domain logic MUST be SAR-specific.
- **Type Safety**: `StrEnum` for constants. No magic strings.

## 3. Technical Constraints & Assumptions

- **Architecture Decision**: `Sentinel1Search` is a state bag (mirrors `Sentinel2Search`), and SAR STAC calls are made via a standalone function `sentinel_1_search(...)` that uses `StacSearch` directly — matching the S2 pattern.
- **`sar:polarizations` Query Operator**: `sar:polarizations` is a list property; queries must use the STAC `contains` operator per polarization, not `eq`. Example: `{"sar:polarizations": {"contains": "VV"}}`.
- **Casing Invariant**: STAC property values for `sar:polarizations` are uppercase (`VV`, `VH`). PC asset keys are lowercase (`vv`, `vh`). These are distinct enums and must never be conflated.
- **Default Instrument Mode**: Default `instrument_mode` must use `PlanetaryComputerS1InstrumentMode.IW`, not a raw string.
- **`sar:product_type`**: `sar:product_type` is out of scope; document as a known variant (GRDH/GRDM/GRDF) but do not filter on it.
- **Single Pol**: Some products lack `vh` polarization. Code must not assume dual-pol everywhere.

## 4. Acceptance Criteria

- [ ] SAR constants in `constants.py` are correct (`vv`/`vh` lowercase, STAC properties, and the three new value enums exist with correct values).
- [ ] `sentinel_1.py` exists with `AbstractSentinel1` and `Sentinel1Search`.
- [ ] `AbstractSentinel1` explicitly rejects/omits optical properties like `max_cloud_cover`.
- [ ] `AbstractSentinel1` accepts spatial filter kwargs `bbox` and `intersects`.
- [ ] `AbstractSentinel1` cannot be instantiated directly (requires `@abstractmethod`).
- [ ] `Sentinel1Search` correctly builds queries using the `contains` operator for polarizations.
- [ ] Unit and integration tests pass.

## 5. Dependencies

- Planetary Computer STAC API.
- `geospatial_tools.stac.core.StacSearch`.

## 6. Out of Scope

- `sar:product_type` sub-variants (GRDH/GRDM/GRDF).
- Sentinel-1 RTC collection (`sentinel-1-rtc`).
- SLC data.
- S1 on Copernicus catalog.
- S1 data downloading/processing (STAC search only).

## 7. Verification Plan

- **Unit Testing**:
    - Test all six `StrEnum` S1 constants in `tests/test_planetary_computer_constants.py`.
    - Test `Sentinel1Search` initialization and query building in `tests/test_planetary_computer_sentinel1.py`.
- **Integration Testing**:
    - STAC query using `Sentinel1Search` validating returned SAR properties.
    - Pin AOI to `bbox=[-122.5, 47.5, -122.0, 48.0]` (Seattle region, dense S1 coverage).
    - Pin date range to `2023-01-01/2023-01-31`.
    - Mark test with `@pytest.mark.integration` and document skip: `pytest -m "not integration"`.
