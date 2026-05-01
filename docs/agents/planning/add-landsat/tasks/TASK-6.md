# TASK-6: Asset-Host Reconnaissance + Auth + Safe `_download_assets` Branch

Maps to **Plan Step 6**.

## Goal

(1) Implement the USGS EROS M2M auth flow, (3) refactor `utils.download_url` for streaming safety, and (4) extend the `download_stac_asset` dispatcher with a session-aware `usgs_landsat` branch.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§2.1 Asset Access, §4 step 6)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2, §3)
- **Memory note:** `usgs_landsat_auth.md` — prior incident where naive `requests.get()` on `landsatlook.usgs.gov` wrote the EROS login HTML to disk with status 200.
- **Code:** `src/geospatial_tools/stac/core.py:379` (`download_stac_asset`), `src/geospatial_tools/stac/core.py:713` (`StacSearch._download_assets`), `src/geospatial_tools/utils.py:177` (`download_url`).

## Subtasks

### 6.1 USGS EROS M2M Auth

- Create `src/geospatial_tools/stac/usgs_landsat/auth.py` exporting:
    - `get_usgs_credentials(logger)` — reads `USGS_USERNAME` and `USGS_TOKEN` (M2M application token, NOT account password) from env. TTY/headless rules identical to URS variant.
    - `get_usgs_m2m_token(logger) -> str` — POST to `https://m2m.cr.usgs.gov/api/api/json/stable/login-token` with body `{"username": ..., "token": ...}`. Return the session token.
    - `build_usgs_session(logger) -> requests.Session` — session pre-loaded with `X-Auth-Token` header and an overridden `rebuild_auth` that preserves the header across redirects to `*.usgs.gov`.

### 6.2 Safety Refactor of `utils.download_url`

- Modify `src/geospatial_tools/utils.py:download_url` (currently uses `response.content`, no streaming, no content-type check) to:
    - Accept an optional `session: requests.Session | None = None` parameter (default `requests`-module-level call to preserve existing call sites).
    - Issue `session.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)` (or `requests.get(...)` when no session).
    - Call `response.raise_for_status()` immediately.
    - **Reject `text/html` responses:** if `response.headers.get("Content-Type", "").startswith("text/html")` → log error, raise `ValueError`, no bytes written.
    - Stream into `<filename>.partial` (path: `Path(filename).with_suffix(filename.suffix + ".partial")`) using `iter_content(chunk_size=8 * 1024 * 1024)`.
    - On clean stream exit, `Path.rename` `<filename>.partial` → `<filename>`. On any exception, attempt `partial.unlink(missing_ok=True)`.
- All existing callers (`download_stac_asset` http branch, anywhere else) inherit the safety upgrade transparently.

### 6.3 `download_stac_asset` Dispatch Extension

- Extend `src/geospatial_tools/stac/core.py:download_stac_asset` (`core.py:379`):
    - Add `method = "usgs_landsat"` branch.
    - New parameter: `session: requests.Session | None = None`. When `method == "usgs_landsat"`, call the refactored `download_url(session=session, ...)`.
    - Existing `"http"` and `"s3"` branches unchanged in semantics.

### 6.4 `_download_assets` UsgsLandsat Branch

- Extend `StacSearch._download_assets` (`core.py:713-761`):
    - When `self.catalog_name == USGS_LANDSAT`: build the auth session via `build_usgs_landsat_session` (or `build_usgs_session`) once per call, set `method = "usgs_landsat"`, pass `session=session` through to `download_stac_asset`. Do NOT set `headers` on this branch — auth lives in the session.
    - Existing `COPERNICUS` and default `http` branches unchanged.

### 6.5 Unit Tests — `tests/test_usgs_landsat_auth.py`

- Mock `requests.Session`, `requests.get`, and `sys.stdin.isatty`. Cover:
    - Headless missing credentials → raises.
    - TTY missing credentials → prompts (mock `getpass`/`input`).
    - HTML response (`Content-Type: text/html`) → `download_url` raises `ValueError`, no `.partial` left behind.
    - 401/403 → `raise_for_status()` propagates.
    - `SessionWithHeaderRedirection.rebuild_auth` preserves header across `urs.usgs_landsat.nasa.gov` redirects (or USGS variant) and strips for unrelated hosts.
    - Streaming: chunked write produces correct file, `.partial` renamed, exception during stream cleans up `.partial`.

## Requirements & Constraints

- Do not save HTML login pages as assets, ever.
- All paths via `pathlib.Path`.
- Atomic chunked streaming writes (`.partial` suffix + rename).
- No silent failures: every failure mode logs at `ERROR` and raises.
- Stdlib `logging` (consistent with surrounding modules).
- Keep `download_url` backward-compatible with existing callers (signature additive only).

## Acceptance Criteria (AC)

- TASK-6 Recon Log subsection added to this file with verbatim curl trace and chosen auth branch.
- `usgs_landsat/auth.py` matches the chosen branch (URS or EROS or none) and handles credential resolution safely in headless mode.
- Refactored `download_url` streams to `.partial`, validates content-type, and renames atomically.
- `download_stac_asset` accepts `method="usgs_landsat"` and a `session` parameter.
- `StacSearch._download_assets` routes UsgsLandsat items through the session-aware path.
- Unit tests cover all auth failure modes, HTML rejection, TTY logic, and streaming/atomic-rename behavior.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 6 - usgs_landsat asset-host recon, auth, and streaming download branch"`
5. Update document: Mark as COMPLETE.
