# 🎯 1. Objective

Implement constants for Planetary Computer Sentinel-2 STAC catalog. Replace magic strings to provide type safety. Match `copernicus/constants.py` pattern, extending it to STAC properties used in queries.

# 🏗️ 2. Architectural Approach

Create `src/geospatial_tools/stac/planetary_computer/constants.py`. Define `PlanetaryComputerS2Collection`, `PlanetaryComputerS2Band`, and `PlanetaryComputerS2Property` enums. Inherit from `enum.StrEnum` (Python 3.11+ standard). Do not use legacy `str, Enum` pattern. Do not override `__str__` or `__repr__` natively handled by `StrEnum`.

Planetary Computer uses plain base names (e.g., `"B02"`) for band asset keys (unlike Copernicus resolution suffix). `PlanetaryComputerS2Band` is simple: no `at_res()` method, no `native_res` property.

`PlanetaryComputerS2Property` eliminates hardcoded STAC query properties (`eo:cloud_cover`, `s2:mgrs_tile`, `s2:nodata_pixel_percentage`). STAC API `sortby` requires full JSON path prefix: `"properties.eo:cloud_cover"`. Enum exposes `sortby_field` property returning `f"properties.{self.value}"` (eliminating secondary magic strings).

# 🧪 3. Verification & Failure Modes

**Verification:**
Write unit tests for enum string representation. Test STAC search with enum bands and properties. Run `make TEST_ARGS='tests/test_stac.py' test-specific`. Run `mypy`.

**Failure Modes:**
Wrong asset keys → STAC API rejects request.
Wrong property keys → STAC search returns empty or fails.
Using legacy `str, Enum` → Type checker warnings, poor modernization.

# 🛠️ 4. Implementation Steps

1. Create `src/geospatial_tools/stac/planetary_computer/constants.py` with `StrEnum`s for collection, bands, and properties. Add `sortby_field` property. Export from `__init__.py`.
2. Add unit tests in `tests/test_planetary_computer_constants.py`.
3. Update `AbstractSentinel2` and `BestProductsForFeatures` default `collection` to `PlanetaryComputerS2Collection.L2A`. Update type hint to `PlanetaryComputerS2Collection | str`.
4. Update `sentinel_2_complete_tile_search` to use `PlanetaryComputerS2Property` for `query` keys, `filter_no_data`, and `sortby_field` for sort field path.
5. Update `download_and_process_sentinel2_asset` default `collections` to `PlanetaryComputerS2Collection.L2A`. Update type hint.
6. Run full QA suite (`make test`, `make lint`) to verify no regressions.

# 🚀 5. Next Step

Approve Step 1?
