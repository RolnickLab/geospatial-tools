# TASK-6: Implement USGS Landsat Online Download Verification Gate

## Goal

Prove the end-to-end anonymous-HTTPS download contract by actually downloading at least one Landsat band asset via `StacSearch._download_assets`'s default `method = "http"` branch. This is the regression gate per plan §2.1: if USGS migrates assets behind signed URLs, this test must fail loudly.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md (Step 6, §2.1 Download-Path Integration)
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md (§7 Online Tests)
- **Existing Code**:
    - `tests/test_copernicus.py` (reference for `@pytest.mark.online` usage)
    - `src/geospatial_tools/stac/core.py:730` (`_download_assets` default `method = "http"` branch)

## Subtasks

1. [ ] Create `tests/test_usgs_landsat_online.py`.
2. [ ] Write a test that:
    - Performs a `Landsat8Search` (or `Landsat9Search`) for a small ROI/time window known to return at least one item.
    - Picks the smallest practical asset (e.g. `qa_pixel`) of a single item.
    - Calls the wrapper's download path so bytes flow through `StacSearch._download_assets`'s default `method = "http"` branch (no `StacSearch` or `_download_assets` patching).
    - Opens the downloaded file with `rasterio` and asserts (a) the file is non-empty and (b) the driver is `GTiff`.
3. [ ] Mark the test(s) with `@pytest.mark.online`.

## Requirements & Constraints

- Use the smallest practical asset; do not download a full multi-band scene.
- Must not require AWS credentials (do **not** use `alternate.s3.href`; out of scope per plan §2.1).
- Must not patch `StacSearch` or `_download_assets`.
- Use the `tmp_path` fixture for the download target so files are cleaned up automatically.
- Must be excluded from the default `make test` run (filtered out by the `online` marker) and runnable on demand via `pytest -m online`.

## Acceptance Criteria (AC)

- [ ] At least one Landsat band asset is successfully downloaded via the default HTTP branch.
- [ ] Downloaded file opens as a valid, non-empty GeoTIFF (verified via `rasterio`: driver `GTiff`, non-zero size).
- [ ] All tests carry the `@pytest.mark.online` marker.
- [ ] No occurrence of `mock`/`patch` against `StacSearch` or `_download_assets` in the test file.

## Testing & Validation

- **Command**: `uv run pytest -m online tests/test_usgs_landsat_online.py`
- **Success State**: Download succeeds and the GeoTIFF validation assertions pass.
- **Manual Verification**: Run `make precommit`, `make pylint`, `make mypy` on the test file.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "test: task 6 - add USGS landsat online download verification gate"`
6. [ ] Update this document: Mark as COMPLETE.
