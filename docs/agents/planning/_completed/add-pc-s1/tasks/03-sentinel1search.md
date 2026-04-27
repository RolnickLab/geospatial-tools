# TASK-3: Implement Sentinel1Search Wrapper and Integration Test

## Goal

Implement `Sentinel1Search(AbstractSentinel1)` to execute the search and download logic. The `search()` method will dynamically build the STAC query using the instance's builder state. Verify with unit tests (mocked `StacSearch`) and a pinned integration test.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` (from Task 2) — `AbstractSentinel1`.
    - `src/geospatial_tools/stac/core.py` — `StacSearch.search`, `StacSearch.download_search_results`, `Asset`.
    - `src/geospatial_tools/stac/planetary_computer/constants.py` — all six S1 enums.

## Subtasks

1. [x] Implement `Sentinel1Search` inheriting from `AbstractSentinel1`. The subclass itself adds no new `__init__` parameters.
2. [x] **`search()`** (and dynamic query building) — TDD.
    - [x] Write failing unit tests (Red) for query building inside `search()`:
        - Emits `{"sar:instrument_mode": {"eq": "IW"}}` when `self.instrument_modes` has one element.
        - Emits `{"sar:instrument_mode": {"in": ["IW", "EW"]}}` when `self.instrument_modes` has multiple elements.
        - Emits `{"sar:polarizations": {"contains": "VV"}}` or similar valid STAC array syntax when `self.polarizations` is set.
        - Emits `{"sat:orbit_state": {"eq": "ascending"}}` or `{"in": ["ascending", "descending"]}` for `self.orbit_states`.
        - Merges with `self.custom_query_params`.
        - Omits keys entirely when states are `None`.
    - [x] Implement `search()` (Green). Construct the `query` dict from the internal state, call `self.client.search` with stored date/spatial kwargs + query, store results in `self.search_results`, and return them.
3. [x] **`download()`** — TDD.
    - [x] Write failing unit test A (Red) — auto-search: `self.search_results is None`. Patch both `self.client.search` and `self.client.download_search_results`. Call `Sentinel1Search(...).download(...)`. Assert `search` was called once, `download_search_results` called with correct `bands`.
    - [x] Write failing unit test B (Red) — already-searched: assert `search` was NOT called if `self.search_results` is populated.
    - [x] Write failing unit test C (Red) — single-pol: `bands=[PlanetaryComputerS1Band.VV]`. Assert lowercase conversion.
    - [x] Implement `download()` (Green).
4. [x] **Integration test** — `@pytest.mark.integration`.
    - [x] Instantiate `Sentinel1Search` with:
        - `date_range="2023-01-01/2023-01-31"`
        - `bbox=(-74.0, 45.4, -73.5, 45.7)` (Montreal region, dense S1 coverage)
    - [x] Apply builder methods:
        - `.filter_by_instrument_mode(PlanetaryComputerS1InstrumentMode.IW)`
        - `.filter_by_polarization([PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH])`
    - [x] Call `.search()`. Assert results non-empty; every item has `properties["sar:instrument_mode"] == "IW"` and `"VV" in properties["sar:polarizations"]`.
    - [x] Document skip flag in a module-level comment: `pytest -m "not integration"`.

## Requirements & Constraints

- Query building logic resides within `search()`.
- Handle list states correctly (e.g., using `in` for multiple `instrument_modes` or `orbit_states`). For `polarizations`, handle PC STAC API array-query requirements (e.g., using `contains` on the first element if multiple are not supported, and documenting this limitation).
- `search()` must use `self.client.search` (single range).
- `download()` must trigger `search()` when `self.search_results is None`.
- No standalone module-level `sentinel_1_search(...)` function. All behavior lives on the class.

## Acceptance Criteria (AC)

- [x] `search()` dynamically builds the STAC query dict: `in` or `eq` on `instrument_mode` / `orbit_state`, appropriate operator for `polarizations`, omitted keys when `None`.
- [x] `search()` unit test passes: `self.client.search` called with stored kwargs + built query, `self.search_results` populated.
- [x] `download()` auto-search unit test passes.
- [x] `download()` cached-results unit test passes.
- [x] `download()` single-pol unit test passes (`bands=["vv"]`).
- [x] Integration test returns non-empty items matching the builder filters.
- [x] Integration test uses `@pytest.mark.integration`, pinned `bbox=(-74.0, 45.4, -73.5, 45.7)`, pinned `date_range="2023-01-01/2023-01-31"`.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py -m "not integration"`
- **Integration**: `pytest tests/test_planetary_computer_sentinel1.py -m integration`
- **Success State**: All unit tests pass without network; integration test passes against live PC STAC API.

## Completion Protocol

1. [x] All ACs are met.
2. [x] Tests pass without regressions.
3. [x] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [x] Documentation updated (if applicable) — add the uppercase-property / lowercase-asset invariant to `KNOWLEDGE.md` if not already captured.
5. [x] Commit work: `git commit -m "feat(stac-pc): implement Sentinel1Search wrapper and builder search execution"`
6. [x] Update this document: Mark as COMPLETE.
