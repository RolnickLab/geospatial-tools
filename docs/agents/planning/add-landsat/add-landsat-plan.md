# Formal Design Document — Add Landsat 8 & 9 (NASA CMR STAC, USGS_EROS provider)

## 1. 🎯 Scope & Context

Add support for searching and downloading Landsat 8 and 9 **Level-1 Collection 2** imagery (calibrated digital numbers; TOA reflectance is computed downstream from MTL.txt rescaling coefficients and is NOT pre-computed in Level-1 assets).

Provide fluent builder interface for Landsat data, matching `AbstractStacWrapper` pattern. Planetary Computer only exposes Landsat 8/9 Level-2 (Surface Reflectance). Use **NASA CMR STAC catalog, USGS_EROS provider** (`https://cmr.earthdata.nasa.gov/stac/USGS_EROS/`).

**Hard constraint:** EarthData (CMR) STAC catalog. Do not switch to alternative catalogs.

## 2. 🧠 Architectural Approach (Trade-offs & Strategy)

- **New STAC Catalog:** Add CMR provider-scoped catalog wiring to `src/geospatial_tools/stac/core.py`. Default URL points at `USGS_EROS` provider (`https://cmr.earthdata.nasa.gov/stac/USGS_EROS/`). The CMR root (`/stac/`) only lists 60+ providers and is not an item-search endpoint for our needs.
- **Facade + Proxy Pattern:** Inherit `Landsat8Search` and `Landsat9Search` from `AbstractStacWrapper`. Point underlying `StacSearch` at the new `EARTHDATA` catalog (single shared collection, platform property differentiates 8 vs 9).
- **`AbstractStacWrapper` refactor:** Current `core.py:904` hardcodes `StacSearch(PLANETARY_COMPUTER)` in the parent `__init__`. Refactor to accept `catalog_name: str = PLANETARY_COMPUTER` so subclasses do not create-then-discard a Planetary Computer client. Default keeps Sentinel-1/2/3 wrappers backward-compatible.
- **`StacSearch` S3 client side-effect:** `core.py:432-433` initializes an S3 client only for `COPERNICUS`. New catalog must not trigger this.
- **Unified Base Class:** Create `AbstractLandsat` to host shared platform-query logic. Single concrete enum value for collection (one shared collection for both platforms).
- **Explicit Enum Constants:** Add `EarthdataLandsatCollection`, `EarthdataLandsatProperty`, and `EarthdataLandsatBand` to `src/geospatial_tools/stac/earthdata/constants.py`. Pin asset/band keys via pre-implementation research (fetch one item, record verbatim).
- **Strict Conventions:** All path manipulations via `pathlib.Path`. Logging via stdlib `logging.Logger` to match existing `core.py`/`utils.py`/`copernicus/auth.py` (project `CLAUDE.md` mentions `structlog` but existing module is stdlib; do not mix). Use explicit keyword arguments for complex calls.

## 2.1 🌐 NASA CMR STAC Catalog Specs

### Endpoint & Protocol

- **CMR root:** `https://cmr.earthdata.nasa.gov/stac/` (lists providers; not used for searches in this feature)
- **Provider-scoped catalog (default):** `https://cmr.earthdata.nasa.gov/stac/USGS_EROS/`
- **Search endpoint:** `GET`/`POST https://cmr.earthdata.nasa.gov/stac/USGS_EROS/search`
- **Collections endpoint:** `https://cmr.earthdata.nasa.gov/stac/USGS_EROS/collections`

### Collections (verified 2026-04-30 against `https://cmr.earthdata.nasa.gov/stac/USGS_EROS/collections`)

- **Single shared L1 collection (both L8 and L9):** STAC `id = "Landsat Level-1 Collection 2_Collection 2"`
- Platform differentiation via STAC core property: `properties.platform ∈ {"LANDSAT_8", "LANDSAT_9"}`

### Search Authentication

- **Required:** No. Provider catalog, `/collections`, `/search`, and item endpoints respond anonymously.
- **Implication:** `create_earthdata_catalog()` calls `pystac_client.Client.open(EARTHDATA_API)` with the standard retry wrapper. No auth header on the catalog client.

### Asset Access — UNVERIFIED, REQUIRES PRE-IMPLEMENTATION CHECK

**Current understanding (NOT verified):** `USGS_EROS` provider asset hrefs likely point to USGS infrastructure (`landsatlook.usgs.gov` or similar), which redirects to **EROS Login (`ers.cr.usgs.gov`)**, NOT NASA URS. The prior memory note `usgs_landsat_auth.md` (2026-04-28) confirmed this for direct `landsatlook.usgs.gov/stac-server` items — naive `requests.get()` writes the EROS login HTML to disk with status 200.

**Mandatory gating step before TASK-6 implementation** (added as TASK-0 / TASK-1 prerequisite check):

1. Issue an anonymous `Landsat8Search` for a small bbox + recent date range against `cmr.earthdata.nasa.gov/stac/USGS_EROS/`.
2. Pick one item, list its asset hrefs verbatim.
3. Run `curl -sIL <href>` and observe the redirect chain. Record the **final** `Content-Type` and final hostname.
4. Branch the auth design based on observed host:
    - **`urs.earthdata.nasa.gov` (NASA URS / EDL):** env vars `EARTHDATA_USERNAME` / `EARTHDATA_PASSWORD`, `SessionWithHeaderRedirection` pattern (subclass `requests.Session`, override `rebuild_auth` to preserve Authorization header on redirects to/from `urs.earthdata.nasa.gov`).
    - **`ers.cr.usgs.gov` (USGS EROS):** env vars `USGS_USERNAME` / `USGS_TOKEN` (M2M application token), POST to `https://m2m.cr.usgs.gov/api/api/json/stable/login-token`, use returned token as `X-Auth-Token` header. Redirect-following only safe with explicit Authorization preservation as well.
    - **Direct asset (`Content-Type: image/tiff` no auth):** unlikely given CMR/USGS history; if observed, just use plain HTTP path with content-type guard.

**Until step 4 is settled, all auth-related sub-implementations remain conditional. The plan's variable naming (`EARTHDATA_USERNAME` etc.) is a placeholder pending verification.**

### Asset Download — Required Behaviors (regardless of auth host)

- **Headless Safety:** If credentials missing, prompt only when `sys.stdin.isatty()` is true; otherwise raise `ValueError`/`RuntimeError` to fail fast in CI.
- **Memory Safety:** `stream=True` with chunked writes (e.g. 8 MiB blocks) — Landsat scenes are multi-GB.
- **Atomic Writes:** Stream to `<final_path>.partial`, rename only on success. All paths via `pathlib.Path`.
- **Content-Type Validation:** Assert response final `Content-Type` is not `text/html`. Call `raise_for_status()`. This must run **before** any bytes are written.
- **Refactor scope:** `src/geospatial_tools/utils.py:download_url` (line ~177) currently uses `response.content` (full body in RAM, no streaming, no content-type check) — **fix this function**, not just add a new branch. Then the Earthdata branch only adds session/auth on top.

## 3. 🛡️ Verification & Failure Modes (FMEA)

- **Pre-implementation gating:** Asset href reconnaissance (see §2.1). Block all auth code until host confirmed.
- **Test Strategy:**
    - Register `integration` and `online` pytest markers in `pyproject.toml` (pre-existing tech debt — current tests use them but they are unregistered, triggering `PytestUnknownMarkWarning`).
    - Unit tests for STAC core wiring (mock `pystac_client.Client.open`).
    - Unit tests for `EarthdataLandsatCollection` / `EarthdataLandsatProperty` / `EarthdataLandsatBand` enum values.
    - Unit tests for `AbstractLandsat` query construction (assert platform filter present without network).
    - Unit tests for auth handling: TTY check, missing credentials in headless mode, HTML response rejection.
    - Integration tests (`@pytest.mark.integration`) for real CMR USGS_EROS searches (no asset bytes).
    - Online tests (`@pytest.mark.online`) for credentialed download path; skip cleanly when env vars missing.
- **Data Integrity:** Chunked atomic streaming writes (`.partial`). Validate downloaded file opens via `rasterio` as `GTiff`.
- **Auth Failures:** Raise explicit exceptions on 401/403, on `Content-Type: text/html`, and on missing credentials in headless mode. Never swallow exceptions.

## 4. 📋 Granular Implementation Steps

| Step | Description                                                                                                                      | Task File   |
| ---- | -------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| 0    | **Prerequisites:** register pytest markers, add `requests` as explicit dependency.                                               | `TASK-0.md` |
| 1    | **Core STAC wiring:** add `EARTHDATA` catalog (USGS_EROS provider URL), `create_earthdata_catalog`, dispatch entry, retry tests. | `TASK-1.md` |
| 2    | **Constants:** pin collection ID, properties, bands (after one-time CMR item inspection).                                        | `TASK-2.md` |
| 3    | **Refactor `AbstractStacWrapper`** to accept `catalog_name`; implement `AbstractLandsat`.                                        | `TASK-3.md` |
| 4    | **Concrete classes:** `Landsat8Search`, `Landsat9Search`. Hardcode `platform` property filter.                                   | `TASK-4.md` |
| 5    | **Integration tests** (live CMR search, no downloads).                                                                           | `TASK-5.md` |
| 6    | **Asset href reconnaissance + auth + safe `_download_assets` branch.** Refactor `utils.download_url` for streaming/safety.       | `TASK-6.md` |
| 7    | **Online tests:** credentialed download verification, GeoTIFF integrity check.                                                   | `TASK-7.md` |
| —    | **Validation:** every task ends with `make precommit && make pylint && make test && make mypy`.                                  | per task    |
| —    | **Init export:** included as TASK-4 subtask 4 (`src/geospatial_tools/stac/earthdata/__init__.py`).                               | TASK-4      |
