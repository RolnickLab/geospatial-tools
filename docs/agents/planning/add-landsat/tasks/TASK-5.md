# TASK-5: Implement USGS Landsat Integration Tests

## Goal

Verify the end-to-end functionality of `Landsat8Search` and `Landsat9Search` against the live USGS STAC API.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md
- **Existing Code**: `tests/test_planetary_computer_sentinel3.py` (reference for integration tests)

## Subtasks

1. [ ] Create `tests/test_usgs_landsat_integration.py`.
2. [ ] Write an integration test for `Landsat8Search`:
    - Perform a real search using a temporal and spatial bounding box.
    - Assert that results are returned.
    - Assert that the returned items have `item.properties["platform"] == "LANDSAT_8"`.
    - Assert that expected Level-1 TOA asset keys (e.g. `red`, `blue`, `qa_pixel`) are present in `item.assets`.
3. [ ] Write an integration test for `Landsat9Search` with identical assertions.
4. [ ] **Download verification gate**: download one small band asset (e.g. `qa_pixel` or a single coastal/blue tile) for one item via the default `method = "http"` branch of `StacSearch._download_assets`. Assert the downloaded file is non-empty and a valid GeoTIFF (e.g. open with `rasterio` and check the driver). This proves the anonymous-HTTPS contract end-to-end and is the regression gate if USGS later moves to signed URLs (see plan §2.1).
5. [ ] Mark all integration tests in this file with `@pytest.mark.integration`.

## Requirements & Constraints

- Tests must use live network calls against `https://landsatlook.usgs.gov/stac-server`.
- Tests must be excluded from the default `make test` run (filtered out by the `integration` marker) and runnable on demand via `pytest -m integration`.
- Download verification must use the smallest practical asset to keep the test bounded; do not download a full multi-band scene.
- Must not require AWS credentials (do not use `alternate.s3.href`; out of scope per plan §2.1).

## Acceptance Criteria (AC)

- [ ] Live search returns actual items from USGS STAC.
- [ ] Asset keys match the constants defined in `TASK-2`.
- [ ] `platform` property is strictly enforced.
- [ ] At least one band asset is successfully downloaded via the default HTTP branch and validated as a non-empty GeoTIFF.
- [ ] All integration tests carry the `@pytest.mark.integration` marker.

## Testing & Validation

- **Command**: `uv run pytest -m integration tests/test_usgs_landsat_integration.py`.
- **Success State**: Real search succeeds, metadata assertions pass, and the download verification gate produces a valid GeoTIFF.
- **Manual Verification**: Review `make precommit`, `make pylint`, `make mypy` on the test file.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "test: task 5 - add USGS landsat integration tests"`
6. [ ] Update this document: Mark as COMPLETE.
