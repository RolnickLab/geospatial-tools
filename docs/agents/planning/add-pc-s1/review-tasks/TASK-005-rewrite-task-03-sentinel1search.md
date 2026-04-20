# TASK-005: Rewrite tasks/03-sentinel1search.md with decided architecture, single-pol handling, and deterministic integration test

## 1. Goal

Produce a corrected implementation task for `Sentinel1Search` and `sentinel_1_search()` that
pins the architecture (state bag + standalone function), specifies `build_query()` implementation,
handles single-pol gracefully, and defines a deterministic, markable integration test.

## 2. Context & References

- **Review findings:** Issues 1, 6, 9, 11 in `docs/agents/planning/add-pc-s1/review.md`

- **Upstream tasks:** TASK-004 — `AbstractSentinel1` interface with `build_query()` and `bbox`/`intersects`. TASK-003 — value enum types.

- **Key files:**

    - `docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md` — file to replace
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — `sentinel_2_complete_tile_search` function as the pattern to mirror
    - `src/geospatial_tools/stac/core.py` — `StacSearch.search()` and `StacSearch.search_for_date_ranges()`

- **Relevant skills:** `python`, `geospatial`, `tdd`

- **Interface contracts (inline):**

    ```python
    # From TASK-004 (AbstractSentinel1)
    class AbstractSentinel1(ABC):
        @abstractmethod
        def build_query(self) -> dict[str, Any]: ...

    # Sentinel1Search — state bag, mirrors Sentinel2Search
    class Sentinel1Search(AbstractSentinel1):
        """State bag for S1 GRD STAC search parameters."""
        def build_query(self) -> dict[str, Any]:
            """Returns STAC query dict using `contains` per polarization."""
            query: dict[str, Any] = {
                PlanetaryComputerS1Property.INSTRUMENT_MODE: {"eq": self.instrument_mode},
            }
            for pol in (self.polarizations or []):
                query[PlanetaryComputerS1Property.POLARIZATIONS] = {"contains": str(pol)}
            if self.orbit_state:
                query[PlanetaryComputerS1Property.ORBIT_STATE] = {"eq": str(self.orbit_state)}
            return query

    # Standalone STAC function — mirrors sentinel_2_complete_tile_search
    def sentinel_1_search(
        collection: str,
        date_ranges: list[str],
        instrument_mode: PlanetaryComputerS1InstrumentMode | str = PlanetaryComputerS1InstrumentMode.IW,
        polarizations: list[PlanetaryComputerS1Polarization] | None = None,
        orbit_state: PlanetaryComputerS1OrbitState | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        intersects: dict | None = None,
        limit: int = 100,
    ) -> list[pystac.Item]:
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

    **Single-pol handling:** Iterate `polarizations` in `build_query()`. Log `WARNING` if a
    requested polarization key is absent in a returned `item.assets` at download time (same
    pattern as `core._download_assets` line 739).

    **Integration test AOI / date (pinned):**

    - `bbox = [-122.5, 47.5, -122.0, 48.0]` (Seattle; dense S1 IW coverage)
    - `date_ranges = ["2023-01-01/2023-01-31"]`
    - Marker: `@pytest.mark.integration`
    - Skip in CI: `pytest -m "not integration"`

## 3. Subtasks

- [x] 1. Update §Goal: "Implement `Sentinel1Search` (state bag) and `sentinel_1_search()` (standalone STAC function), wire `build_query()` with `contains` operators, handle single-pol gracefully, and verify with a pinned integration test."
- [x] 2. Add subtask: "Write failing unit test for `Sentinel1Search.build_query()` verifying `contains` operator is used for each polarization and `eq` for `instrument_mode` (TDD Red)."
- [x] 3. Add subtask: "Write failing unit test for `Sentinel1Search.build_query()` verifying `orbit_state` is omitted from query when `None` (TDD Red)."
- [x] 4. Add subtask: "Implement `Sentinel1Search.build_query()` until unit tests pass (TDD Green)."
- [x] 5. Add subtask: "Write failing unit test for `sentinel_1_search()`: mock `StacSearch`, assert it is called with the correct `query` dict (TDD Red)."
- [x] 6. Add subtask: "Implement `sentinel_1_search()` until unit test passes (TDD Green)."
- [x] 7. Add subtask: "Write `@pytest.mark.integration` test: call `sentinel_1_search()` with pinned Seattle bbox + Jan 2023 date range; assert returned items are non-empty and each has `properties['sar:instrument_mode'] == 'IW'`."
- [x] 8. Add §Requirements & Constraints constraint: "`sar:polarizations` must use `contains` operator, not `eq`. See review issue #1."
- [x] 9. Add §Requirements & Constraints constraint: "Single-pol case: `build_query()` must not crash when `polarizations=['VV']` (no VH). Asset download silently skips absent keys — same as `core._download_assets`."
- [x] 10. Update §Acceptance Criteria to include: `contains` operator verified in unit test; `sentinel_1_search()` mock test passes; integration test returns non-empty items with correct `instrument_mode`; single-pol unit test passes.
- [x] 11. Update §Testing & Validation with exact pytest commands and expected output.
- [x] 12. Update commit message to `feat(stac-pc): implement Sentinel1Search and sentinel_1_search`.

## 4. Requirements & Constraints

- **Technical:** Markdown document only — no code changes in this task.
- **Business:** Rewritten `03-sentinel1search.md` must be self-contained. All interface contracts above must appear inline.
- **Out of scope:** `KNOWLEDGE.md` update (handled in TASK-006). SLC or RTC variants.

## 5. Acceptance Criteria

- [x] AC-1: Rewritten `03-sentinel1search.md` includes `Sentinel1Search.build_query()` signature inline with `contains` operator.
- [x] AC-2: Task includes `sentinel_1_search()` standalone function signature inline.
- [x] AC-3: Task has TDD Red/Green subtasks for both `build_query()` and `sentinel_1_search()` unit tests.
- [x] AC-4: Integration test entry specifies `bbox=[-122.5, 47.5, -122.0, 48.0]`, `date_ranges=["2023-01-01/2023-01-31"]`, and `@pytest.mark.integration`.
- [x] AC-5: Task §Requirements states single-pol must not crash.
- [x] AC-6: Commit message in §Completion Protocol uses `feat(stac-pc):` scope.

## 6. Testing & Validation

```bash
# Verify mandatory content in the rewritten task
grep -n "contains" docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
grep -n "sentinel_1_search" docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
grep -n "pytest.mark.integration" docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
grep -n "\-122\.5" docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
grep -n "2023-01-01" docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
grep -n "single.pol\|single_pol\|polarizations=\[.VV.\]" docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
```

Expected: each grep returns at least one match.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm each grep returns at least one match.
3. Stage and commit:
    ```bash
    git add docs/agents/planning/add-pc-s1/tasks/03-sentinel1search.md
    git commit -m "docs(stac-pc): rewrite task-03 Sentinel1Search with arch decision and integration test — closes TASK-005"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-006.
