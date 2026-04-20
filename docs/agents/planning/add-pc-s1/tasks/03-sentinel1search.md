# TASK-3: Implement Sentinel1Search and sentinel_1_search

## 1. Goal

Implement `Sentinel1Search` (state bag, extends `AbstractSentinel1`) and the standalone function
`sentinel_1_search()` (mirrors `sentinel_2_complete_tile_search`). Wire `build_query()` with
`contains` operators for `sar:polarizations`, handle single-pol products without crashing, and
verify end-to-end behaviour with a pinned, deterministic integration test.

## 2. Context & References

- **Source Plan**: `docs/agents/planning/add-pc-s1/add-pc-s1.md`

- **Relevant Specs**: `docs/agents/planning/add-pc-s1/add-pc-s1-spec.md`

- **Upstream tasks**:

    - TASK-1 — six S1 enums in `constants.py` (`PlanetaryComputerS1Property`,
        `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`,
        `PlanetaryComputerS1OrbitState`)
    - TASK-2 — `AbstractSentinel1` with `@abstractmethod build_query()` in `sentinel_1.py`

- **Key files**:

    - `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` — append `Sentinel1Search` and
        `sentinel_1_search()` to this file
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — `sentinel_2_complete_tile_search`
        is the exact pattern to mirror
    - `src/geospatial_tools/stac/core.py` — `StacSearch.search_for_date_ranges()` is the call target
    - `tests/test_planetary_computer_sentinel1.py` — extend with new unit and integration tests

- **Relevant skills**: `python`, `geospatial`, `tdd`

- **Interface contracts (complete, inline):**

    ```python
    import pystac
    from typing import Any

    from geospatial_tools.stac.core import PLANETARY_COMPUTER, StacSearch
    from geospatial_tools.stac.planetary_computer.constants import (
        PlanetaryComputerS1Collection,
        PlanetaryComputerS1InstrumentMode,
        PlanetaryComputerS1OrbitState,
        PlanetaryComputerS1Polarization,
        PlanetaryComputerS1Property,
    )


    class Sentinel1Search(AbstractSentinel1):
        """State bag for Sentinel-1 GRD STAC search parameters on Planetary Computer.

        Mirrors Sentinel2Search: stores parameters, implements build_query().
        Actual STAC calls are made via sentinel_1_search().
        """

        def build_query(self) -> dict[str, Any]:
            """Build the STAC query dict for this S1 search configuration.

            Uses `contains` operator per polarization — sar:polarizations is stored
            as a list in STAC items; `eq` would match the whole list and fail.

            Returns:
                STAC API query extension dict.
            """
            query: dict[str, Any] = {
                PlanetaryComputerS1Property.INSTRUMENT_MODE: {"eq": str(self.instrument_mode)},
            }
            for pol in (self.polarizations or []):
                query[PlanetaryComputerS1Property.POLARIZATIONS] = {"contains": str(pol)}
            if self.orbit_state is not None:
                query[PlanetaryComputerS1Property.ORBIT_STATE] = {"eq": str(self.orbit_state)}
            return query


    def sentinel_1_search(
        collection: str,
        date_ranges: list[str],
        instrument_mode: PlanetaryComputerS1InstrumentMode | str = PlanetaryComputerS1InstrumentMode.IW,
        polarizations: list[PlanetaryComputerS1Polarization] | None = None,
        orbit_state: PlanetaryComputerS1OrbitState | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        intersects: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> list[pystac.Item]:
        """Search for Sentinel-1 GRD STAC items on Planetary Computer.

        Mirrors sentinel_2_complete_tile_search: builds query via Sentinel1Search,
        executes via StacSearch.search_for_date_ranges().

        Args:
            collection: S1 collection ID (use PlanetaryComputerS1Collection.GRD).
            date_ranges: List of date range strings.
            instrument_mode: SAR instrument mode. Defaults to IW.
            polarizations: Polarizations to filter on. None means no filter.
            orbit_state: Orbit direction filter. None means no filter.
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat). None means no filter.
            intersects: GeoJSON geometry filter. None means no filter.
            limit: Max items per page. Defaults to 100.

        Returns:
            List of pystac.Item objects matching the search criteria.
        """
        client = StacSearch(PLANETARY_COMPUTER)
        searcher = Sentinel1Search(
            collection=collection,
            instrument_mode=instrument_mode,
            polarizations=polarizations,
            orbit_state=orbit_state,
            bbox=bbox,
            intersects=intersects,
        )
        query = searcher.build_query()
        return client.search_for_date_ranges(
            date_ranges=date_ranges,
            collections=collection,
            bbox=bbox,
            intersects=intersects,
            query=query,
            limit=limit,
        )
    ```

    **Single-pol handling:** `build_query()` iterates `self.polarizations or []` — passing
    `polarizations=["VV"]` works without crash. At asset download time, missing asset keys
    (e.g. `"vh"` absent) are logged at `WARNING` and skipped — same pattern as
    `core._download_assets` (line 739: `if band not in item.assets: ... continue`).

    **Integration test (pinned):**

    - AOI: `bbox=(-122.5, 47.5, -122.0, 48.0)` (Seattle; dense S1 IW GRD coverage)
    - Date range: `["2023-01-01/2023-01-31"]`
    - Collection: `PlanetaryComputerS1Collection.GRD`
    - Marker: `@pytest.mark.integration`
    - CI skip: `pytest -m "not integration"`

## 3. Subtasks

- [ ] 1. Write failing unit test: `Sentinel1Search([VV, VH]).build_query()` returns a dict where
    `sar:polarizations` key uses `{"contains": "VV"}` and `{"contains": "VH"}` (or iterates),
    and `sar:instrument_mode` uses `{"eq": "IW"}` (TDD Red).
- [ ] 2. Write failing unit test: `Sentinel1Search(orbit_state=None).build_query()` does NOT
    contain key `sat:orbit_state` (TDD Red).
- [ ] 3. Write failing unit test for single-pol: `Sentinel1Search(polarizations=["VV"]).build_query()`
    does not raise (TDD Red).
- [ ] 4. Implement `Sentinel1Search.build_query()` until subtasks 1–3 tests pass (TDD Green).
- [ ] 5. Write failing unit test for `sentinel_1_search()`: mock `StacSearch`, call
    `sentinel_1_search(collection=..., date_ranges=..., polarizations=["VV", "VH"])`, assert
    `search_for_date_ranges` was called with a `query` dict containing `contains` (TDD Red).
- [ ] 6. Implement `sentinel_1_search()` until subtask 5 test passes (TDD Green).
- [ ] 7. Write `@pytest.mark.integration` test calling `sentinel_1_search()` with pinned Seattle
    bbox and Jan 2023 date range; assert result is non-empty and every item has
    `properties["sar:instrument_mode"] == "IW"`.
- [ ] 8. Run `ruff check` and `mypy` — fix any issues (Refactor).

## 4. Requirements & Constraints

- **`sar:polarizations` must use `contains`, not `eq`.** The STAC property is a list; `eq` fails
    for partial matches. Each polarization gets its own `{"contains": "<POL>"}` entry.
- **Single-pol must not crash.** `build_query()` with `polarizations=["VV"]` (no VH) must return
    a valid query dict without raising.
- **`orbit_state=None` means no filter.** Omit `sat:orbit_state` from the query entirely.
- **Standalone function pattern.** `Sentinel1Search` does NOT call `StacSearch` directly. Only
    `sentinel_1_search()` instantiates `StacSearch`. This mirrors `Sentinel2Search` /
    `sentinel_2_complete_tile_search`.
- **Typing.** All parameters and return types annotated. `polarizations` uses
    `list[PlanetaryComputerS1Polarization] | None`, not `list[str] | None`.
- **Out of scope.** S1 downloading/processing, SLC, RTC (`sentinel-1-rtc`). `KNOWLEDGE.md`
    update — that is TASK-6.

## 5. Acceptance Criteria

- [ ] AC-1: `Sentinel1Search(polarizations=[VV, VH]).build_query()` returns a dict with
    `{"sar:polarizations": {"contains": ...}}` entry — verified by unit test.
- [ ] AC-2: `Sentinel1Search(instrument_mode=IW).build_query()` returns
    `{"sar:instrument_mode": {"eq": "IW"}}` — verified by unit test.
- [ ] AC-3: `Sentinel1Search(orbit_state=None).build_query()` does not contain key
    `sat:orbit_state` — verified by unit test.
- [ ] AC-4: `Sentinel1Search(polarizations=["VV"]).build_query()` does not raise — single-pol
    unit test passes.
- [ ] AC-5: `sentinel_1_search()` mock test passes — `StacSearch.search_for_date_ranges` called
    with the query dict produced by `build_query()`.
- [ ] AC-6: Integration test `@pytest.mark.integration` with `bbox=(-122.5, 47.5, -122.0, 48.0)`
    and `date_ranges=["2023-01-01/2023-01-31"]` returns non-empty results with
    `properties["sar:instrument_mode"] == "IW"` on every item.
- [ ] AC-7: All new code passes `ruff check` and `mypy` with zero errors.
- [ ] AC-8: `pytest tests/test_planetary_computer_sentinel1.py -x` passes; integration tests
    skippable with `pytest -m "not integration"`.

## 6. Testing & Validation

```bash
# Unit tests only
pytest tests/test_planetary_computer_sentinel1.py -v -m "not integration"

# Full suite including integration (requires network)
pytest tests/test_planetary_computer_sentinel1.py -v

# Type-check
mypy src/geospatial_tools/stac/planetary_computer/sentinel_1.py

# Lint
ruff check src/geospatial_tools/stac/planetary_computer/sentinel_1.py

# Regression guard — full test suite
pytest -x -m "not integration"
```

Expected: unit tests green without network; integration test green with network access to
Planetary Computer; `mypy`/`ruff` exit 0; no regressions in the rest of the suite.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm expected output.
3. Stage and commit:
    ```bash
    git add src/geospatial_tools/stac/planetary_computer/sentinel_1.py \
            tests/test_planetary_computer_sentinel1.py
    git commit -m "feat(stac-pc): implement Sentinel1Search and sentinel_1_search — closes TASK-3"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-6
    (`KNOWLEDGE.md` update).
