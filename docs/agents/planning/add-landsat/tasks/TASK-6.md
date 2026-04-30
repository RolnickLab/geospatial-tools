# TASK-6: Implement Earthdata Auth + `_download_assets` Branch

## Goal

Implement Earthdata Login (EDL) authentication flow to download Landsat assets. STAC asset `href` redirects to NASA EDL service.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

### 6.1 Earthdata Auth

- Create `src/geospatial_tools/stac/earthdata/auth.py`:
    - `get_earthdata_credentials(logger)` — reads `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` from env; falls back to prompt.
    - Implement auth logic to handle EDL redirects (e.g., via `.netrc` or `requests.Session`).

### 6.2 `_download_assets` Earthdata branch

- Extend `src/geospatial_tools/stac/core.py` `_download_assets` to add Earthdata branch:
    - Inject credentials/session configured in `auth.py`.
    - Perform streaming download to `<name>.partial`.
    - **CRITICAL**: Assert response `Content-Type` is not `text/html`. Raise explicit exception if HTML, preventing silent save of login page.
    - Rename `.partial` to final filename on success.

### 6.3 Unit tests

- Add `tests/test_earthdata_auth.py` mocking `requests`:
    - Mock failure modes (401 unauthorized, HTML response from target).
    - Verify exception raised on `text/html` content type.

## Requirements & Constraints

- Do not save HTML login pages as assets.
- Use atomic streaming writes (`.partial` suffix).

## Acceptance Criteria (AC)

- `earthdata/auth.py` handles credential resolution.
- `StacSearch._download_assets` routes Earthdata items to authenticated flow and writes via atomic `.partial` files.
- Explicit exception raised if response is HTML.
- Unit tests cover auth failure modes.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 6 - add Earthdata auth and download branch"`
5. Update document: Mark as COMPLETE.
