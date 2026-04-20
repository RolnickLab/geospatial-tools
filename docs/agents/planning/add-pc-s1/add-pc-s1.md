# 1. 🎯 Scope & Context

Sentinel-1 is SAR (active microwave). Cloud cover and optical-nodata semantics do not apply. Filtering dimensions are polarization, instrument mode, and orbit state. We are adding this data source to the Planetary Computer STAC client.

# 2. 🏗️ Architectural Approach

Create `AbstractSentinel1` and `Sentinel1Search` in `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`. `Sentinel1Search` is a state bag (mirrors `Sentinel2Search`); SAR STAC calls go through a standalone function `sentinel_1_search(tile_id, collection, date_ranges, instrument_mode, polarizations, orbit_state, bbox)` using `StacSearch` — matching the `sentinel_2_complete_tile_search` pattern.
Use `StrEnum` in `constants.py` for all six enum types: `PlanetaryComputerS1Collection`, `PlanetaryComputerS1Property`, `PlanetaryComputerS1Band`, `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, `PlanetaryComputerS1OrbitState`.

# 3. 🛡️ Verification & FMEA

**Verification:**

- Unit tests for all S1 constants.
- Unit tests for `Sentinel1Search` init and query building.
- Integration test for PC STAC S1 GRD products (using `pytest.mark.integration`, pinned AOI `bbox=[-122.5, 47.5, -122.0, 48.0]`, and pinned date range `2023-01-01/2023-01-31`).

**Failure Modes:**

- STAC API failure. Handled by `StacSearch`.
- Polarization mismatch. Some S1 products are single pol (VV only). Code must handle missing `vh` asset without crashing.
- Invalid CRS. Handled by `geospatial_tools`.

# 4. 📝 Implementation Steps

1. Add all six SAR enum types to `src/geospatial_tools/stac/planetary_computer/constants.py`.
    *Commit: `feat(stac-pc): add sentinel-1 constants for planetary computer`*
2. Create `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` and implement `AbstractSentinel1` with `@abstractmethod build_query()`, taking SAR and spatial kwargs (`bbox`, `intersects`).
    *Commit: `feat(stac-pc): implement AbstractSentinel1 base class`*
3. Implement `Sentinel1Search` state bag and the `sentinel_1_search()` standalone function handling STAC queries using `contains` operator for polarizations.
    *Commit: `feat(stac-pc): implement Sentinel1Search and sentinel_1_search`*
4. Create unit and integration tests in `tests/test_planetary_computer_sentinel1.py`.
    *Commit: `test(stac-pc): add tests for sentinel-1 search`*

# 5. 🔄 Next Step

Do you approve Step 1?
