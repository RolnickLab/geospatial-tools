# TASK-5: Implement USGS Landsat Integration Tests (Live Search)

## Goal

Verify that `Landsat8Search` and `Landsat9Search` produce real, non-empty results against the live USGS STAC API **without patching `StacSearch`**. Metadata only — asset-byte downloads live in TASK-6.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md (Step 5)
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md (§7 Integration Tests)
- **Existing Code**: `tests/test_planetary_computer_sentinel3.py` (reference for `@pytest.mark.integration` usage)

## Subtasks

1. [ ] Create `tests/test_usgs_landsat_integration.py`.
2. [ ] Write an integration test for `Landsat8Search`:
    - Perform a real search using a temporal and spatial bounding box. Do **not** patch or mock `StacSearch`.
    - Assert that results are returned.
    - Assert that the returned items have `item.properties["platform"] == "LANDSAT_8"`.
    - Assert that expected Level-1 TOA asset keys (e.g. `red`, `blue`, `qa_pixel`) are present in `item.assets` (key check only — no bytes pulled).
3. [ ] Write an integration test for `Landsat9Search` with identical assertions against `LANDSAT_9`.
4. [ ] Mark all tests in this file with `@pytest.mark.integration`.

## Requirements & Constraints

- Tests must use live network calls against `https://landsatlook.usgs.gov/stac-server`.
- Tests must **not** patch or mock `StacSearch` — that is the boundary being verified.
- Tests must be excluded from the default `make test` run (filtered out by the `integration` marker) and runnable on demand via `pytest -m integration`.
- Must **not** download asset bytes (no `_download_assets` calls). Byte-level download is TASK-6.

## Acceptance Criteria (AC)

- [ ] Live search returns actual items from USGS STAC for both Landsat 8 and Landsat 9.
- [ ] Asset keys match the constants defined in TASK-2.
- [ ] `platform` property is strictly enforced.
- [ ] All tests carry the `@pytest.mark.integration` marker.
- [ ] No occurrence of `mock`/`patch` against `StacSearch` in the test file.

## Testing & Validation

- **Command**: `uv run pytest -m integration tests/test_usgs_landsat_integration.py`
- **Success State**: Real search succeeds and metadata assertions pass.
- **Manual Verification**: Run `make precommit`, `make pylint`, `make mypy` on the test file.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "test: task 5 - add USGS landsat integration tests (live search)"`
6. [ ] Update this document: Mark as COMPLETE.
