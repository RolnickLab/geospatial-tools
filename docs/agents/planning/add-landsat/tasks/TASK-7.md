# TASK-7: Online Download Verification Gate

Maps to **Plan Step 7**. Depends on **TASK-6**.

## Goal

Verify the end-to-end credentialed download contract by downloading a single Landsat band asset through the Earthdata branch of `StacSearch._download_assets`, and validate the file integrity.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§3, §4 step 7)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§7)
- **Auth contract:** Pinned by TASK-6 reconnaissance (URS or USGS EROS). Env-var names finalized there.

## Subtasks

1. Create `tests/test_earthdata_landsat_online.py`.
2. Use the env-var names finalized in TASK-6 (most likely `EARTHDATA_USERNAME`/`EARTHDATA_PASSWORD` OR `USGS_USERNAME`/`USGS_TOKEN`). Add a module-level skip:
    ```python
    import os
    import pytest

    _CREDS_VAR_1 = "EARTHDATA_USERNAME"  # or USGS_USERNAME — pinned in TASK-6
    _CREDS_VAR_2 = "EARTHDATA_PASSWORD"  # or USGS_TOKEN — pinned in TASK-6

    pytestmark = [
        pytest.mark.online,
        pytest.mark.skipif(
            not (os.getenv(_CREDS_VAR_1) and os.getenv(_CREDS_VAR_2)),
            reason=f"{_CREDS_VAR_1} and {_CREDS_VAR_2} required for online download test",
        ),
    ]
    ```
3. Write `test_landsat_download_via_earthdata_branch(tmp_path)`:
    - Construct `Landsat8Search` (or `Landsat9Search`) with a small bbox + recent date range. Call `.search()`. Assert ≥1 item.
    - Pick the first item.
    - Pick exactly ONE band to download (smallest available — e.g. `qa_pixel` or a low-res QA band — to keep test runtime/data volume bounded).
    - Call the wrapper's `download(...)` with `base_directory=tmp_path` so bytes flow through `_download_assets` Earthdata branch (NO patching of `StacSearch` or `download_url`).
    - Assert returned `Asset` has one `AssetSubItem` with `filename` pointing inside `tmp_path`.
    - Assert no `<filename>.partial` left behind.
    - Assert `rasterio.open(filename)` succeeds and `.driver == "GTiff"`.

## Requirements & Constraints

- Do NOT use S3 alternate paths.
- Do NOT patch `StacSearch`, `_download_assets`, `download_url`, or `download_stac_asset`.
- Use `tmp_path` fixture; verify via `pathlib.Path` ops only.
- Pick a single small band to keep the test under reasonable time/bandwidth (~tens of MB max).

## Acceptance Criteria (AC)

- Landsat band asset downloaded via the Earthdata branch.
- Downloaded file opens as a valid `GTiff`.
- Test skips cleanly when credentials unset (no failure, no error).
- Test carries `@pytest.mark.online` marker.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "test: task 7 - add online Landsat download verification gate"`
5. Update document: Mark as COMPLETE.
