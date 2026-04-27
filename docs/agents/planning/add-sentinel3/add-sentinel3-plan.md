# Formal Design Document: Add Sentinel-3 OLCI Constants

## 1. Overview

This task adds Sentinel-3 OLCI constants to `src/geospatial_tools/stac/planetary_computer/constants.py`. Focus is Top of Atmosphere (TOA) data and Near-Infrared (NIR) / Water Vapour bands (Oa16 to Oa21).

## 2. Rationale

Current STAC constants support Sentinel-1 and Sentinel-2. Extending support to Sentinel-3 OLCI enables automated STAC queries for ocean and land color applications. TOA data requires specific radiance band definitions.

## 3. Architecture & Implementation

### 3.1. Add Collection Constants

Create `PlanetaryComputerS3Collection` inheriting from `StrEnum`.

- `OLCI_L1B = "sentinel-3-olci-l1b-efr"` (TOA Radiance proxy).
- `OLCI_WFR = "sentinel-3-olci-wfr-l2-netcdf"` (L2 Reflectance).

### 3.2. Add Band Constants

Create `PlanetaryComputerS3Band` inheriting from `StrEnum`. Add requested TOA bands and complementary near-infrared / water-vapour absorption bands.

- `OA16 = "oa16-radiance"` (778.75 nm)
- `OA17 = "oa17-radiance"` (865 nm)
- `OA18 = "oa18-radiance"` (885 nm)
- `OA19 = "oa19-radiance"` (900 nm)
- `OA20 = "oa20-radiance"` (940 nm)
- `OA21 = "oa21-radiance"` (1020 nm)

Add common aliases:

- `NIR_865 = "oa17-radiance"`
- `WATER_VAPOUR = "oa19-radiance"`

### 3.3. Add Property Constants

Create `PlanetaryComputerS3Property` inheriting from `StrEnum`.

- `ORBIT_STATE = "sat:orbit_state"`

### 3.4. Create `Sentinel3Search` Class

Create `src/geospatial_tools/stac/planetary_computer/sentinel_3.py`.
Implement `Sentinel3Search` inheriting from `AbstractStacWrapper`.

- Implement `__init__` supporting S3 collections (`OLCI_WFR` by default).
- Implement `filter_by_orbit_state` method similar to S1.
- Implement `_build_collection_query` to apply `ORBIT_STATE` filter.
- Implement `download` method to download assets. S3 bands in Planetary Computer are lowercase by default, similar to S1, so ensure band keys are handled correctly.

## 4. Testing Strategy

- Add tests in `tests/test_planetary_computer_constants.py` to verify enum values map exactly to required Planetary Computer asset keys.
- Ensure `PlanetaryComputerS3Band` alias values equal their target enum values.
- Add tests in `tests/test_planetary_computer_sentinel3.py` to verify `Sentinel3Search` query building and state invalidation.
- Run `make precommit`, `make pylint`, `make mypy`, and `make test` to validate code quality and functionality.
