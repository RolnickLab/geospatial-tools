# TASK-7: Implement Earthdata Landsat Online Download Verification Gate

## Goal

Verify end-to-end credentialed download contract by downloading Landsat band asset via Earthdata branch of `StacSearch._download_assets`.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

1. Create `tests/test_earthdata_landsat_online.py`.
2. Write test that:
    - Performs `Landsat8Search` (or `Landsat9Search`) for small ROI/time window returning item.
    - Picks specific asset/band.
    - Calls wrapper's download path so bytes flow through Earthdata branch (no patching).
    - Validates downloaded file: atomic `.partial` rename executed, opens with `rasterio` as `GTiff` (or valid JPEG).
3. Skip test cleanly when `EARTHDATA_USERNAME` / `EARTHDATA_PASSWORD` env vars missing.
4. Mark test(s) with `@pytest.mark.online`.

## Requirements & Constraints

- Do not use S3 alternate paths.
- Do not patch `StacSearch` or `_download_assets`.
- Use `tmp_path` fixture for download target.

## Acceptance Criteria (AC)

- Landsat band asset downloaded via Earthdata branch.
- Downloaded file opens as valid GeoTIFF.
- Test skips when credentials unset.
- Tests carry `@pytest.mark.online` marker.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "test: task 7 - add Earthdata landsat online download verification gate"`
5. Update document: Mark as COMPLETE.
