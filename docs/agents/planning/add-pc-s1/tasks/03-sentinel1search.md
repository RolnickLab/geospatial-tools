# TASK-3: Implement Sentinel1Search and Integration Tests

## Goal

Implement `Sentinel1Search` (state bag) and `sentinel_1_search()` (standalone STAC function), wire `build_query()` with `contains` operators, handle single-pol gracefully, and verify with a pinned integration test.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**: src/geospatial_tools/stac/planetary_computer/sentinel_1.py (from Task 2), src/geospatial_tools/stac/core.py (`StacSearch`)

## Subtasks

1. [ ] Implement `Sentinel1Search` inheriting from `AbstractSentinel1`.
2. [ ] Write failing unit test for `Sentinel1Search.build_query()` verifying `contains` operator is used for each polarization and `eq` for `instrument_mode` (TDD Red).
3. [ ] Write failing unit test for `Sentinel1Search.build_query()` verifying `orbit_state` is omitted from query when `None` (TDD Red).
4. [ ] Implement `Sentinel1Search.build_query()` until unit tests pass (TDD Green).
    ```python
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
    ```
5. [ ] Write failing unit test for `sentinel_1_search()`: mock `StacSearch`, assert it is called with the correct `query` dict (TDD Red).
6. [ ] Implement `sentinel_1_search()` standalone STAC function until unit test passes (TDD Green).
    ```python
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
7. [ ] Write `@pytest.mark.integration` test: call `sentinel_1_search()` with pinned Seattle bbox + Jan 2023 date range; assert returned items are non-empty and each has `properties['sar:instrument_mode'] == 'IW'`.

## Requirements & Constraints

- `sar:polarizations` must use `contains` operator, not `eq`. See review issue #1.
- Single-pol case: `build_query()` must not crash when `polarizations=['VV']` (no VH). Asset download silently skips absent keys — same as `core._download_assets`.

## Acceptance Criteria (AC)

- [ ] `contains` operator verified in unit test for `build_query()`.
- [ ] `sentinel_1_search()` mock test passes.
- [ ] Integration test returns non-empty items with correct `instrument_mode`.
- [ ] Single-pol unit test passes (`polarizations=["VV"]`).
- [ ] Integration test specifies `bbox=[-122.5, 47.5, -122.0, 48.0]`, `date_ranges=["2023-01-01/2023-01-31"]`, and uses `@pytest.mark.integration`.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py`
- **Integration**: `pytest -m integration tests/test_planetary_computer_sentinel1.py`
- **Success State**: All tests pass.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat(stac-pc): implement Sentinel1Search and sentinel_1_search"`
6. [ ] Update this document: Mark as COMPLETE.
