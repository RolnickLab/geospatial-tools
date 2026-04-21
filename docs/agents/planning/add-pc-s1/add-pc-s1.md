# 1. 🎯 Scope & Context

Sentinel-1 is SAR (active microwave). Cloud cover and optical-nodata semantics do not apply. Filtering dimensions are polarization, instrument mode, and orbit state. We are adding this data source to the Planetary Computer STAC client as a thin, synchronous utility wrapper — deliberately simpler than the S2 tile-coverage workflow.

# 2. 🏗️ Architectural Approach

Create `AbstractSentinel1` and `Sentinel1Search` in `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.

`Sentinel1Search` **is** the wrapper: it owns a `StacSearch(PLANETARY_COMPUTER)` instance via composition and exposes three methods — `build_query()`, `search()`, `download(bands, base_directory)`. No module-level search function. No multi-date-range iteration (use pystac's native `"start/end"` date-range string; callers loop externally if they need disjoint ranges).

`AbstractSentinel1` declares `@abstractmethod build_query() -> dict[str, Any]` so direct instantiation raises `TypeError`. It stores SAR kwargs (`collection`, `instrument_mode`, `polarizations`, `orbit_state`), spatial kwargs (`bbox`, `intersects`), the single `date_range`, the `StacSearch` client, and two result-state attributes (`search_results`, `downloaded_assets`).

All six SAR `StrEnum` types live in `constants.py`: `PlanetaryComputerS1Collection`, `PlanetaryComputerS1Property`, `PlanetaryComputerS1Band`, `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, `PlanetaryComputerS1OrbitState`.

# 3. 🛡️ Verification & FMEA

**Verification:**

- Unit tests for all S1 constants.
- Unit tests for `Sentinel1Search` init, `build_query()`, `search()`, and `download()` (mocking `StacSearch`).
- Integration test for PC STAC S1 GRD products (`@pytest.mark.integration`, pinned AOI `bbox=(-122.5, 47.5, -122.0, 48.0)`, pinned date range `"2023-01-01/2023-01-31"`).

**Failure Modes:**

- STAC API failure — handled by `StacSearch` retry loop.
- Polarization mismatch — STAC `query` extension allows one `contains` per property, so `build_query()` filters on `polarizations[0]` only. Callers needing strict "all pols present" post-filter `self.search_results`. Documented in the `build_query()` docstring.
- Single-pol product missing `vh` asset during download — `StacSearch._download_assets` already logs-and-skips absent keys. No new handling needed; tests confirm the pathway.
- Invalid CRS — handled upstream in `geospatial_tools`.

# 4. 📝 Implementation Steps

1. **[COMPLETE]** Add all six SAR enum types to `src/geospatial_tools/stac/planetary_computer/constants.py`.
    *Commit: `feat(stac-pc): add S1 constants`*
2. Create `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` and implement `AbstractSentinel1` with `@abstractmethod build_query()`, SAR kwargs, spatial kwargs (`bbox: BBoxLike`, `intersects: IntersectsLike`), single `date_range: DateLike`, `self.client`, `self.search_results`, `self.downloaded_assets`.
    *Commit: `feat(stac-pc): implement AbstractSentinel1 base class`*
3. Implement `Sentinel1Search(AbstractSentinel1)` with three methods: `build_query()` (using `contains` on `polarizations[0]`), `search()` (wraps `self.client.search`), and `download(bands, base_directory)` (wraps `self.client.download_search_results`, triggers `search()` if needed).
    *Commit: `feat(stac-pc): implement Sentinel1Search wrapper`*
4. Create unit + integration tests in `tests/test_planetary_computer_sentinel1.py`.
    *Commit: `test(stac-pc): add tests for sentinel-1 search`*

# 5. 🔄 Next Step

Step 1 is complete. Next: Step 2 — implement `AbstractSentinel1`. Awaiting approval.
