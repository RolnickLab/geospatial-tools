# SPEC: Planetary Computer Sentinel-1 GRD Support

## 1. Overview

- **Goal**: Add Sentinel-1 (S1) GRD STAC client.
- **Problem Statement**: PC STAC client missing S1 GRD. Blindly copying Sentinel-2 design fails because S1 is SAR. SAR ignores clouds. Need SAR-specific classes and constants.

## 2. Requirements

### Functional Requirements

- [ ] Add `PlanetaryComputerS1Collection` (`sentinel-1-grd`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Property` (`sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`) to `constants.py`.
- [ ] Add `PlanetaryComputerS1Band` (`vv`, `vh` - lowercase) to `constants.py`.
- [ ] Create `AbstractSentinel1` in `sentinel_1.py`. Requires SAR kwargs (`instrument_mode="IW"`, `polarizations=["VV", "VH"]`). NO CLOUD COVER.
- [ ] Create `Sentinel1Search` extending `AbstractSentinel1`.

### Non-Functional Requirements

- **Consistency**: Base structure mimics S2 (e.g., initialization pattern), but domain logic MUST be SAR-specific.
- **Type Safety**: `StrEnum` for constants. No magic strings.

## 3. Technical Constraints & Assumptions

- **Existing systems**: Use `geospatial_tools.stac.core.StacSearch`.
- **Assumptions**:
    - Some products lack `vh` polarization. Code must not assume dual-pol everywhere.

## 4. Acceptance Criteria

- [ ] SAR constants in `constants.py` are correct (`vv`/`vh` lowercase, proper STAC property keys).
- [ ] `sentinel_1.py` exists with `AbstractSentinel1` and `Sentinel1Search`.
- [ ] `AbstractSentinel1` explicitly rejects/omits optical properties like `max_cloud_cover`.
- [ ] `Sentinel1Search` correctly filters by `instrument_mode` and `polarizations`.
- [ ] Unit and integration tests pass.

## 5. Dependencies

- Planetary Computer STAC API.
- `geospatial_tools.stac.core.StacSearch`.

## 6. Out of Scope

- Sentinel-1 SLC data.
- S1 in Copernicus catalog.
- S1 data downloading/processing (STAC search only).

## 7. Verification Plan

- **Unit Testing**:
    - Test `StrEnum` S1 constants in `tests/test_planetary_computer_constants.py`.
    - Test `Sentinel1Search` initialization and query building in `tests/test_planetary_computer_sentinel1.py`.
- **Integration Testing**:
    - STAC query using `Sentinel1Search` validating returned SAR properties (e.g., checking `sar:instrument_mode` is `IW`).
