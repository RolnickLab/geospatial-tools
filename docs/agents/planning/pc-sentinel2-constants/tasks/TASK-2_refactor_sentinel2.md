# TASK-2: Refactor Sentinel-2 Module

## Goal

Update `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` using new Planetary Computer constants. Eliminate hardcoded STAC magic strings.

## Context & References

- **Source Plan**: `docs/agents/planning/pc-sentinel2-constants/pc-sentinel2-constants-plan.md`
- **Relevant Specs**: `docs/agents/planning/pc-sentinel2-constants/pc-sentinel2-constants-spec.md`
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py`

## Subtasks

1. [ ] Import `PlanetaryComputerS2Collection`, `PlanetaryComputerS2Property` in `sentinel_2.py`.
2. [ ] Update `AbstractSentinel2.__init__` default `collection` to `PlanetaryComputerS2Collection.L2A`. Update type hint to `PlanetaryComputerS2Collection | str`.
3. [ ] Update `BestProductsForFeatures.__init__` default `collection` to `PlanetaryComputerS2Collection.L2A`. Update type hint to `PlanetaryComputerS2Collection | str`.
4. [ ] Update `download_and_process_sentinel2_asset` default `collections` to `PlanetaryComputerS2Collection.L2A`. Update type hint to `PlanetaryComputerS2Collection | str`.
5. [ ] Refactor `sentinel_2_complete_tile_search` `query` dict keys using `PlanetaryComputerS2Property.CLOUD_COVER` and `PlanetaryComputerS2Property.MGRS_TILE`.
6. [ ] Refactor `sentinel_2_complete_tile_search` `sortby` field using `PlanetaryComputerS2Property.CLOUD_COVER.sortby_field`.
7. [ ] Refactor `sentinel_2_complete_tile_search` `filter_no_data` using `PlanetaryComputerS2Property.NODATA_PIXEL_PERCENTAGE`.
8. [ ] Refactor `optimal_result.properties[...]` accesses in `sentinel_2_complete_tile_search` using `PlanetaryComputerS2Property` keys.
9. [ ] Run integration tests (`make TEST_ARGS='tests/test_stac.py' test-specific`).
10. [ ] Run full QA suite (`make test`, `make lint`).

## Requirements & Constraints

- Do not modify core `StacSearch` logic in `core.py`.
- Do not modify vector or raster processing logic.
- Type hints MUST be updated alongside default values (`PlanetaryComputerS2Collection | str`).
- Do **not** fix `print(error)` at `sentinel_2.py:320` (out of scope).
- `sortby` field uses `PlanetaryComputerS2Property.CLOUD_COVER.sortby_field`.

## Acceptance Criteria (AC)

- [ ] AC 1: `AbstractSentinel2.__init__` default `collection` is `PlanetaryComputerS2Collection.L2A` with type `PlanetaryComputerS2Collection | str`.
- [ ] AC 2: `BestProductsForFeatures.__init__` default `collection` is `PlanetaryComputerS2Collection.L2A` with type `PlanetaryComputerS2Collection | str`.
- [ ] AC 3: `download_and_process_sentinel2_asset` default `collections` is `PlanetaryComputerS2Collection.L2A` with type `PlanetaryComputerS2Collection | str`.
- [ ] AC 4: `sentinel_2_complete_tile_search` contains no bare string literals for properties.
- [ ] AC 5: `sentinel_2_complete_tile_search` `sortby` uses `.sortby_field`.
- [ ] AC 6: `mypy` passes with zero errors on `sentinel_2.py`.
- [ ] AC 7: `make TEST_ARGS='tests/test_stac.py' test-specific` passes.
- [ ] AC 8: `make test` passes without regressions.

## Testing & Validation

- **Command**: `make TEST_ARGS='tests/test_stac.py' test-specific`
- **Success State**: All STAC tests pass. No search failures.
- **Manual Verification**: Review `sentinel_2.py` for remaining magic strings.

## Completion Protocol

1. [ ] All ACs met.
2. [ ] Tests pass without regressions.
3. [ ] Code passes formatting, linting, type-checking (zero errors).
4. [ ] Documentation updated.
5. [ ] Commit work: `git commit -m "refactor: task 2 - apply pc constants to sentinel_2.py"`
6. [ ] Update document: Mark as COMPLETE.
