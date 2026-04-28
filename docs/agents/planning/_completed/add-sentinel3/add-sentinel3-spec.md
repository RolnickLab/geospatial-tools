# SPEC: Sentinel-3 OLCI STAC Integration

## 1. Overview

- **Goal**: Add STAC constants and a search wrapper class for Sentinel-3 OLCI data on Planetary Computer.
- **Problem Statement**: Current Planetary Computer STAC support is limited to Sentinel-1 and Sentinel-2. This blocks automated queries for Sentinel-3 data required for ocean and land color applications.

## 2. Requirements

### Functional Requirements

- [ ] Implement `PlanetaryComputerS3Collection` with `OLCI_L1B` (`sentinel-3-olci-l1b-efr`) and `OLCI_WFR` (`sentinel-3-olci-wfr-l2-netcdf`) constants.
- [ ] Implement `PlanetaryComputerS3Band` for TOA/NIR/Water-Vapour bands (`OA16` to `OA21`) mapping to `oaXX-radiance` values, with common aliases (`NIR_865`, `WATER_VAPOUR`).
- [ ] Implement `PlanetaryComputerS3Property` containing `ORBIT_STATE` (`sat:orbit_state`).
- [ ] Implement `Sentinel3Search` class extending `AbstractStacWrapper`.
- [ ] `Sentinel3Search` must support filtering by orbit state.
- [ ] `Sentinel3Search` must ensure band keys are processed in lowercase during download (similar to `Sentinel1Search`).

### Non-Functional Requirements

- Architecture: Must adhere to the existing `AbstractStacWrapper` facade + proxy pattern.

## 3. Technical Constraints & Assumptions

- Existing systems/libraries to use: `StrEnum` (Python 3.11+), `AbstractStacWrapper` from `src/geospatial_tools/stac/core.py`.
- Assumptions: Planetary Computer API relies on specific string keys like `oa17-radiance` for these bands.

## 4. Acceptance Criteria

- [ ] All `PlanetaryComputerS3Collection`, `PlanetaryComputerS3Band`, and `PlanetaryComputerS3Property` enum values match the planned strings exactly.
- [ ] Aliases in `PlanetaryComputerS3Band` (e.g. `NIR_865`) map correctly to their primary band equivalent.
- [ ] `Sentinel3Search` instantiates successfully and defaults to `OLCI_WFR` if no collection is provided.
- [ ] `Sentinel3Search.filter_by_orbit_state` successfully updates internal state and invalidates cached results.
- [ ] `Sentinel3Search._build_collection_query` correctly constructs the STAC API query dictionary for `sat:orbit_state`.

## 5. Dependencies

- Internal modules: `geospatial_tools.stac.core`, `geospatial_tools.geotools_types`.

## 6. Out of Scope

- Adding support for other Sentinel-3 instruments (SLSTR, SRAL, Synergy).
- Custom download logic beyond basic casing normalization before delegating to `AbstractStacWrapper`.

## 7. Verification Plan

- Unit tests in `tests/test_planetary_computer_constants.py` asserting correct string values for S3 constants.
- Unit tests in `tests/test_planetary_computer_sentinel3.py` asserting:
    - Default collection assignment.
    - State invalidation on filter application.
    - Query dictionary structure for single and multiple orbit states (`eq` and `in` operators).
- Execute `make precommit`, `make pylint`, `make mypy`, and `make test` to ensure project QA standards are met.
