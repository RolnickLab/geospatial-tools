# TASK-1: Create Planetary Computer Constants

## Goal

Implement `PlanetaryComputerS2Collection`, `PlanetaryComputerS2Band`, and `PlanetaryComputerS2Property` using `enum.StrEnum`. Write unit tests to verify string representations.

## Context & References

- **Source Plan**: `docs/agents/planning/pc-sentinel2-constants/pc-sentinel2-constants-plan.md`
- **Relevant Specs**: `docs/agents/planning/pc-sentinel2-constants/pc-sentinel2-constants-spec.md`

## Subtasks

1. [x] Create `src/geospatial_tools/stac/planetary_computer/constants.py`.
2. [x] Define `PlanetaryComputerS2Collection` enum inheriting from `enum.StrEnum`. Set `L2A = "sentinel-2-l2a"`.
3. [x] Define `PlanetaryComputerS2Property` enum inheriting from `enum.StrEnum`. Add `CLOUD_COVER = "eo:cloud_cover"`, `MGRS_TILE = "s2:mgrs_tile"`, `NODATA_PIXEL_PERCENTAGE = "s2:nodata_pixel_percentage"`. Add `sortby_field` property returning `f"properties.{self.value}"`.
4. [x] Define `PlanetaryComputerS2Band` enum inheriting from `enum.StrEnum`. Values are plain base names (no resolution suffix). Standard bands: `B01`, `B02`, `B03`, `B04`, `B05`, `B06`, `B07`, `B08`, `B8A`, `B09`, `B11`, `B12`, `SCL`, `TCI`, `AOT`, `WVP`. Common name aliases: `COASTAL=B01`, `BLUE=B02`, `GREEN=B03`, `RED=B04`, `RED_EDGE_1=B05`, `RED_EDGE_2=B06`, `RED_EDGE_3=B07`, `NIR=B08`, `NIR_NARROW=B8A`, `SWIR_1=B11`, `SWIR_2=B12`.
5. [x] Export constants from `src/geospatial_tools/stac/planetary_computer/__init__.py`.
6. [x] Create `tests/test_planetary_computer_constants.py`.
7. [x] Write unit tests to assert exact string values of all enum members.
8. [x] Write unit test to assert `PlanetaryComputerS2Property.CLOUD_COVER.sortby_field == "properties.eo:cloud_cover"`.

## Requirements & Constraints

- Enums MUST inherit from `enum.StrEnum` (Python 3.11+). Do NOT use `str, Enum`. Do NOT override `__str__` and `__repr__`.
- Planetary Computer STAC uses base band names (`"B02"`). Do not append resolutions. No `at_res()` or `native_res`.
- `PlanetaryComputerS2Property` exposes `sortby_field` property (not an enum member) for `"properties.<key>"` format.
- Use only built-in `enum.StrEnum`.

## Acceptance Criteria (AC)

- [x] AC 1: `PlanetaryComputerS2Collection.L2A == "sentinel-2-l2a"`.
- [x] AC 2: `PlanetaryComputerS2Property.CLOUD_COVER == "eo:cloud_cover"`, `MGRS_TILE == "s2:mgrs_tile"`, `NODATA_PIXEL_PERCENTAGE == "s2:nodata_pixel_percentage"`. `PlanetaryComputerS2Property.CLOUD_COVER.sortby_field == "properties.eo:cloud_cover"`.
- [x] AC 3: `PlanetaryComputerS2Band` contains all 16 standard bands and 11 common aliases. `PlanetaryComputerS2Band.BLUE == "B02"`.
- [x] AC 4: New constants importable from `geospatial_tools.stac.planetary_computer`.
- [x] AC 5: Unit tests in `tests/test_planetary_computer_constants.py` pass.

## Testing & Validation

- **Command**: `make TEST_ARGS='tests/test_planetary_computer_constants.py' test-specific`
- **Success State**: All tests pass.
- **Manual Verification**: Review `constants.py` for `StrEnum` inheritance.

## Completion Protocol

1. [x] All ACs met.
2. [x] Tests pass without regressions.
3. [x] Code passes formatting, linting, and type-checking (zero errors).
4. [x] Documentation updated.
5. [x] Commit work: `git commit -m "feat: task 1 - create planetary computer constants"`
6. [x] Update document: Mark as COMPLETE.
