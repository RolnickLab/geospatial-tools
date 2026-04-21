# 1. 🎯 Scope & Context

Sentinel-1 is SAR (active microwave). Cloud cover and optical-nodata semantics do not apply. Filtering dimensions are polarization, instrument mode, and orbit state. We are adding this data source to the Planetary Computer STAC client as a thin, synchronous utility wrapper. We will use a fluent builder pattern to define search parameters, moving away from a single opaque query generation function.

# 2. 🏗️ Architectural Approach

Create `AbstractSentinel1` and `Sentinel1Search` in `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.

`Sentinel1Search` **is** the wrapper: it owns a `StacSearch(PLANETARY_COMPUTER)` instance via composition. The STAC query is represented by the class instance's state.

Instead of a `build_query` method, `AbstractSentinel1` provides fluent builder methods:

- `filter_by_instrument_mode()`
- `filter_by_polarization()`
- `filter_by_orbit_state()`
- `with_custom_query()`

These methods update the instance state (`self.instrument_modes`, `self.polarizations`, etc.) and return `self` to allow chaining. The `search()` method dynamically constructs the final STAC `query` dictionary from these named attributes at execution time. This allows searching for multiple properties at once (e.g., multiple orbit states using the `in` operator) while retaining the flexibility of custom queries.

All six SAR `StrEnum` types live in `constants.py`: `PlanetaryComputerS1Collection`, `PlanetaryComputerS1Property`, `PlanetaryComputerS1Band`, `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, `PlanetaryComputerS1OrbitState`.

# 3. 🛡️ Verification & FMEA

**Verification:**

- Unit tests for all S1 constants.
- Unit tests validating that the builder methods update internal state and return `self`.
- Unit tests verifying that `Sentinel1Search.search()` correctly translates internal state arrays into STAC query dictionaries (e.g., using `in` for lists).
- Integration test for PC STAC S1 GRD products (`@pytest.mark.integration`, pinned AOI `bbox=(-74.0, 45.4, -73.5, 45.7)` (Montreal), pinned date range `"2023-01-01/2023-01-31"`, utilizing the builder methods).

**Failure Modes:**

- STAC API failure — handled by `StacSearch` retry loop.
- Polarization mismatch — STAC `query` extension handles arrays. `search()` must construct valid STAC syntax for multiple polarizations. If limitations exist in the PC STAC API, they will be handled and documented gracefully.
- Single-pol product missing `vh` asset during download — `StacSearch._download_assets` already logs-and-skips absent keys. No new handling needed.
- Invalid CRS — handled upstream in `geospatial_tools`.

# 4. 📝 Implementation Steps

1. **[COMPLETE]** Add all six SAR enum types to `src/geospatial_tools/stac/planetary_computer/constants.py`.
    *Commit: `feat(stac-pc): add S1 constants`*
2. Create `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` and implement `AbstractSentinel1` with spatial kwargs (`bbox: BBoxLike`, `intersects: IntersectsLike`), single `date_range: DateLike`, `self.client`, `self.search_results`, `self.downloaded_assets`. Implement the fluent builder methods (`filter_by_*` and `with_custom_query`) to manage instance state.
    *Commit: `feat(stac-pc): implement AbstractSentinel1 base class with builder pattern`*
3. Implement `Sentinel1Search(AbstractSentinel1)` with two main methods: `search()` (dynamically builds the STAC query dict from instance state and wraps `self.client.search`), and `download(bands, base_directory)` (wraps `self.client.download_search_results`, triggers `search()` if needed).
    *Commit: `feat(stac-pc): implement Sentinel1Search wrapper and search execution`*
4. Create unit + integration tests in `tests/test_planetary_computer_sentinel1.py`.
    *Commit: `test(stac-pc): add tests for sentinel-1 search builder`*

# 5. 🔄 Next Step

Step 2 is complete. Next: Step 3 — implement `Sentinel1Search` wrapper and search execution. Awaiting approval.
aiting approval.
