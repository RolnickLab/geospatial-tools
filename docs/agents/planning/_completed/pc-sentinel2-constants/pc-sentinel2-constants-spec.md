# SPEC: Planetary Computer Sentinel-2 Constants

## 1. Overview

- **Goal**: Implement strongly-typed constants for the Planetary Computer Sentinel-2 STAC catalog. Replace magic strings in the codebase.
- **Problem Statement**: Implementation in `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` relies on hardcoded magic strings for collection names, band names, and STAC query properties. Error-prone, lacks type safety, complicates maintenance.

## 2. Requirements

### Functional Requirements

- [x] Create `src/geospatial_tools/stac/planetary_computer/constants.py` module.
- [x] Define `PlanetaryComputerS2Collection` enum for collection names.
- [x] Define `PlanetaryComputerS2Band` enum for asset band keys.
- [x] Define `PlanetaryComputerS2Property` enum for STAC query properties with a `sortby_field` property.
- [x] Refactor `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` using new enums.
- [x] Export new constants module from `src/geospatial_tools/stac/planetary_computer/__init__.py`.

### Non-Functional Requirements

- **Type Safety**: Enums MUST inherit from `enum.StrEnum` (Python 3.11+). Updated parameters reflect enum type (`collection: PlanetaryComputerS2Collection | str`). Do not use legacy `str, Enum`.
- **Simplicity**: PC band enum uses plain base names (no resolution suffix, no `at_res()` method, no `native_res` property). Do not override `__str__` or `__repr__`.

## 3. Technical Constraints & Assumptions

- **STAC Asset Keys**: Planetary Computer Sentinel-2 STAC uses base band name as asset key (`"B02"`, not `"B02_10m"`).
- **STAC `sortby` field format**: STAC API `sortby` object requires full JSON path `"properties.eo:cloud_cover"`. `PlanetaryComputerS2Property` exposes `sortby_field` property returning `f"properties.{self.value}"`.
- **Libraries**: Use built-in `enum.StrEnum`.

## 4. Acceptance Criteria

- [x] `PlanetaryComputerS2Collection` enum exists. `PlanetaryComputerS2Collection.L2A` == `"sentinel-2-l2a"`.
- [x] `PlanetaryComputerS2Property` enum exists. Contains `CLOUD_COVER = "eo:cloud_cover"`, `MGRS_TILE = "s2:mgrs_tile"`, `NODATA_PIXEL_PERCENTAGE = "s2:nodata_pixel_percentage"`. Its `sortby_field` property returns `f"properties.{self.value}"`.
- [x] `PlanetaryComputerS2Band` enum exists. Inherits from `enum.StrEnum`. Standard bands: `B01`, `B02`, `B03`, `B04`, `B05`, `B06`, `B07`, `B08`, `B8A`, `B09`, `B11`, `B12`, `SCL`, `TCI`, `AOT`, `WVP`. Common name aliases: `COASTAL=B01`, `BLUE=B02`, `GREEN=B03`, `RED=B04`, `RED_EDGE_1=B05`, `RED_EDGE_2=B06`, `RED_EDGE_3=B07`, `NIR=B08`, `NIR_NARROW=B8A`, `SWIR_1=B11`, `SWIR_2=B12`.
- [x] No enum overrides `__str__` or `__repr__`.
- [x] `AbstractSentinel2` default `collection` parameter uses `PlanetaryComputerS2Collection.L2A` with type `PlanetaryComputerS2Collection | str`.
- [x] `BestProductsForFeatures` default `collection` parameter uses `PlanetaryComputerS2Collection.L2A` with type `PlanetaryComputerS2Collection | str`.
- [x] `sentinel_2_complete_tile_search` function uses `PlanetaryComputerS2Property` for all query keys, `filter_no_data`, and `sortby_field` for the sort field path.
- [x] `download_and_process_sentinel2_asset` function uses `PlanetaryComputerS2Collection.L2A` with type `PlanetaryComputerS2Collection | str`.
- [x] New constants exported from `src/geospatial_tools/stac/planetary_computer/__init__.py`.
- [x] Unit tests for new constants pass.
- [x] Full QA suite passes without regressions.

## 5. Dependencies

- Relies on existing `pystac` and STAC search implementations. Built-in `enum.StrEnum` requires Python 3.11+.

## 6. Out of Scope

- Refactoring Sentinel-2 Copernicus constants (`str, Enum` refactor).
- Modifying core `StacSearch` client logic.
- Modifying vector or raster processing logic.
- Fixing `print(error)` forbidden pattern at `sentinel_2.py:320`.

## 7. Verification Plan

- **Unit Tests**: Create `tests/test_planetary_computer_constants.py`. Verify exact string values.
- **Integration Tests**: Run full test suite. Verify STAC workflows un-broken. Verify `test_stac.py` passes. Run `mypy` to verify typing.
