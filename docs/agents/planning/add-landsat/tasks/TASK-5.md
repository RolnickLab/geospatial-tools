# TASK-5: Implement Earthdata Landsat Integration Tests (Live Search)

## Goal

Verify `Landsat8Search` and `Landsat9Search` produce real results against live Earthdata STAC API without patching.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

1. Create `tests/test_earthdata_landsat_integration.py`.
2. Write integration test for `Landsat8Search`: perform real search, assert results, verify platform property and asset keys.
3. Write integration test for `Landsat9Search`.
4. Mark all tests with `@pytest.mark.integration`.

## Requirements & Constraints

- Tests use live network calls against `https://cmr.earthdata.nasa.gov/stac/`.
- Do not patch or mock `StacSearch`.
- Do not download asset bytes.

## Acceptance Criteria (AC)

- Live search returns actual items from Earthdata STAC.
- Asset keys match defined constants.
- Platform property strictly enforced.
- Tests carry `@pytest.mark.integration` marker.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "test: task 5 - add Earthdata landsat integration tests"`
5. Update document: Mark as COMPLETE.
