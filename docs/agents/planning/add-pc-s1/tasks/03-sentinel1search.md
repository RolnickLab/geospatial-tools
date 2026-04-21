# TASK-3: Implement Sentinel1Search Wrapper and Integration Test

## Goal

Implement `Sentinel1Search(AbstractSentinel1)` as a `StacSearch` wrapper: three methods — `build_query()`, `search()`, `download()`. Verify with unit tests (mocked `StacSearch`) and a pinned integration test.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` (from Task 2) — `AbstractSentinel1`.
    - `src/geospatial_tools/stac/core.py` — `StacSearch.search`, `StacSearch.download_search_results`, `Asset`.
    - `src/geospatial_tools/stac/planetary_computer/constants.py` — all six S1 enums.

## Subtasks

1. [ ] Implement `Sentinel1Search` inheriting from `AbstractSentinel1`. The subclass itself adds no new `__init__` parameters; it inherits the signature unchanged.
2. [ ] **`build_query()`** — TDD.
    - [ ] Write failing unit tests (Red):
        - Emits `{"sar:instrument_mode": {"eq": "IW"}}` when `instrument_mode=PlanetaryComputerS1InstrumentMode.IW`.
        - Emits `{"sar:polarizations": {"contains": "VV"}}` when `polarizations=[PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH]` (only the first polarization goes into the query).
        - Omits `sar:polarizations` key entirely when `polarizations=None`.
        - Omits `sat:orbit_state` key entirely when `orbit_state=None`.
        - Emits `{"sat:orbit_state": {"eq": "ascending"}}` when `orbit_state=PlanetaryComputerS1OrbitState.ASCENDING`.
        - Does not crash with `polarizations=["VV"]` (single-pol case).
    - [ ] Implement `build_query()` (Green):
        ```python
        def build_query(self) -> dict[str, Any]:
            """Build a STAC query dict for Sentinel-1 GRD.

            Uses the STAC `query` extension. The `sar:polarizations` field is a
            list property; the `query` extension only supports a single
            `contains` operator per property, so we filter on the first
            polarization in ``self.polarizations``. Callers needing strict
            "all requested polarizations present" semantics should post-filter
            ``self.search_results``.

            Returns:
                The STAC query dictionary.
            """
            query: dict[str, Any] = {
                PlanetaryComputerS1Property.INSTRUMENT_MODE: {"eq": str(self.instrument_mode)},
            }
            if self.polarizations:
                query[PlanetaryComputerS1Property.POLARIZATIONS] = {
                    "contains": str(self.polarizations[0])
                }
            if self.orbit_state:
                query[PlanetaryComputerS1Property.ORBIT_STATE] = {"eq": str(self.orbit_state)}
            return query
        ```
3. [ ] **`search()`** — TDD.
    - [ ] Write failing unit test (Red): patch `self.client.search` with a `MagicMock` returning a list of fake `pystac.Item`. Call `Sentinel1Search(...).search()`. Assert the mock was called once with `date_range=<stored>`, `collections=<stored>`, `bbox=<stored>`, `intersects=<stored>`, `query=<build_query result>`. Assert `self.search_results` equals the mock's return value, and that `search()` returns the same list.
    - [ ] Implement `search()` (Green):
        ```python
        def search(self) -> list[pystac.Item]:
            """Execute the STAC search and cache results on ``self.search_results``."""
            query = self.build_query()
            results = self.client.search(
                date_range=self.date_range,
                collections=self.collection,
                bbox=self.bbox,
                intersects=self.intersects,
                query=query,
            )
            self.search_results = results
            return results
        ```
4. [ ] **`download()`** — TDD.
    - [ ] Write failing unit test A (Red) — auto-search: `self.search_results is None`. Patch both `self.client.search` and `self.client.download_search_results`. Call `Sentinel1Search(...).download(bands=[...], base_directory=tmp_path)`. Assert `search` was called once, `download_search_results` was called once with the expected `bands` and `base_directory`, and `self.downloaded_assets` holds the download mock's return value.
    - [ ] Write failing unit test B (Red) — already-searched: pre-populate `self.search_results`. Patch both mocks. Call `.download(...)`. Assert `search` was NOT called, `download_search_results` WAS called.
    - [ ] Write failing unit test C (Red) — single-pol: `bands=[PlanetaryComputerS1Band.VV]`. Assert `download_search_results` is called with `bands=["vv"]` (string values, lowercase). No crash.
    - [ ] Implement `download()` (Green):
        ```python
        def download(
            self,
            bands: list[PlanetaryComputerS1Band | str],
            base_directory: str | Path,
        ) -> list[Asset]:
            """Download the requested S1 asset bands for cached search results.

            Triggers ``self.search()`` first if ``self.search_results`` is
            ``None``. Absent asset keys (e.g., missing ``vh`` on single-pol
            products) are skipped with a log message by
            ``StacSearch._download_assets``.

            Args:
                bands: Asset band keys to download (lowercase, e.g. ``"vv"``, ``"vh"``).
                base_directory: Download destination.

            Returns:
                List of ``Asset`` objects, one per search result.
            """
            if self.search_results is None:
                self.search()
            band_strs = [str(b) for b in bands]
            assets = self.client.download_search_results(
                bands=band_strs, base_directory=base_directory
            )
            self.downloaded_assets = assets
            return assets
        ```
5. [ ] **Integration test** — `@pytest.mark.integration`.
    - [ ] Instantiate `Sentinel1Search` with:
        - `date_range="2023-01-01/2023-01-31"`
        - `bbox=(-122.5, 47.5, -122.0, 48.0)` (Seattle region, dense S1 coverage)
        - `instrument_mode=PlanetaryComputerS1InstrumentMode.IW`
        - `polarizations=[PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH]`
    - [ ] Call `.search()`. Assert results non-empty; every item has `properties["sar:instrument_mode"] == "IW"` and `"VV" in properties["sar:polarizations"]`.
    - [ ] Do NOT exercise `.download()` in the integration test — asset downloads are expensive and out of scope for CI verification.
    - [ ] Document skip flag in a module-level comment: `pytest -m "not integration"`.

## Requirements & Constraints

- `sar:polarizations` uses `contains` on `polarizations[0]` only — single-key emission, no dict-overwrite loop. Document the limitation in the docstring.
- `search()` must use `self.client.search` (single range), NOT `self.client.search_for_date_ranges`. Multi-range iteration is out of scope for this class.
- `download()` must trigger `search()` when `self.search_results is None`; must not re-search when already populated.
- `Sentinel1Search` does NOT add `__init__` parameters — it uses the inherited signature.
- No standalone module-level `sentinel_1_search(...)` function. All behavior lives on the class.

## Acceptance Criteria (AC)

- [ ] `build_query()` unit tests pass: `contains` on first pol only, `eq` on `instrument_mode` / `orbit_state`, omitted keys when inputs are `None`.
- [ ] `search()` unit test passes: `self.client.search` called with stored kwargs + built query, `self.search_results` populated, return value correct.
- [ ] `download()` auto-search unit test passes.
- [ ] `download()` cached-results unit test passes (does not re-search).
- [ ] `download()` single-pol unit test passes (`bands=["vv"]`).
- [ ] Integration test returns non-empty items with correct `instrument_mode` and `VV` in `sar:polarizations`.
- [ ] Integration test uses `@pytest.mark.integration`, pinned `bbox=(-122.5, 47.5, -122.0, 48.0)`, pinned `date_range="2023-01-01/2023-01-31"`.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py -m "not integration"` (unit tests only)
- **Integration**: `pytest tests/test_planetary_computer_sentinel1.py -m integration` (requires network)
- **Success State**: All unit tests pass without network; integration test passes against live PC STAC API.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable) — add the uppercase-property / lowercase-asset invariant and the `contains`-on-first-pol limitation to `KNOWLEDGE.md` if not already captured.
5. [ ] Commit work: `git commit -m "feat(stac-pc): implement Sentinel1Search wrapper"`
6. [ ] Update this document: Mark as COMPLETE.
