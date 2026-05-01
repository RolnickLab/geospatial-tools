# Formal Design Document — Add Landsat 8 & 9 (NASA CMR STAC, USGS_EROS provider)

## 1. 🎯 Scope & Context

Add support for searching and downloading Landsat 8 and 9 **Level-1 Collection 2** imagery (calibrated digital numbers; TOA reflectance is computed downstream from MTL.txt rescaling coefficients and is NOT pre-computed in Level-1 assets).

Provide fluent builder interface for Landsat data, matching `AbstractStacWrapper` pattern. Planetary Computer only exposes Landsat 8/9 Level-2 (Surface Reflectance). Use **NASA CMR STAC catalog, USGS_EROS provider** (`https://landsatlook.usgs.gov/stac-server`).

**Hard constraint:** UsgsLandsat (CMR) STAC catalog. Do not switch to alternative catalogs.

## 2. 🧠 Architectural Approach (Trade-offs & Strategy)

- **New STAC Catalog:** Add CMR provider-scoped catalog wiring to `src/geospatial_tools/stac/core.py`. Default URL points at `USGS_EROS` provider (`https://landsatlook.usgs.gov/stac-server`). The CMR root (`/stac/`) only lists 60+ providers and is not an item-search endpoint for our needs.
- **Facade + Proxy Pattern:** Inherit `Landsat8Search` and `Landsat9Search` from `AbstractStacWrapper`. Point underlying `StacSearch` at the new `USGS_LANDSAT` catalog (single shared collection, platform property differentiates 8 vs 9).
- **`AbstractStacWrapper` refactor:** Current `core.py:904` hardcodes `StacSearch(PLANETARY_COMPUTER)` in the parent `__init__`. Refactor to accept `catalog_name: str = PLANETARY_COMPUTER` so subclasses do not create-then-discard a Planetary Computer client. Default keeps Sentinel-1/2/3 wrappers backward-compatible.
- **`StacSearch` S3 client side-effect:** `core.py:432-433` initializes an S3 client only for `COPERNICUS`. New catalog must not trigger this.
- **Unified Base Class:** Create `AbstractLandsat` to host shared platform-query logic. Single concrete enum value for collection (one shared collection for both platforms).
- **Explicit Enum Constants:** Add `UsgsLandsatLandsatCollection`, `UsgsLandsatLandsatProperty`, and `UsgsLandsatLandsatBand` to `src/geospatial_tools/stac/usgs_landsat/constants.py`. Pin asset/band keys via pre-implementation research (fetch one item, record verbatim).
- **Strict Conventions:** All path manipulations via `pathlib.Path`. Logging via stdlib `logging.Logger` to match existing `core.py`/`utils.py`/`copernicus/auth.py` (project `CLAUDE.md` mentions `structlog` but existing module is stdlib; do not mix). Use explicit keyword arguments for complex calls.

## 2.1 🌐 NASA CMR STAC Catalog Specs

### Endpoint & Protocol

- **CMR root:** Not applicable (USGS direct)
- **Provider-scoped catalog (default):** `https://landsatlook.usgs.gov/stac-server`
- **Search endpoint:** `GET`/`POST https://landsatlook.usgs.gov/stac-serversearch`
- **Collections endpoint:** `https://landsatlook.usgs.gov/stac-servercollections`

### Collections (verified 2026-04-30 against `https://landsatlook.usgs.gov/stac-servercollections`)

- **Single shared L1 collection (both L8 and L9):** STAC `id = "landsat-c2l1"`
- Platform differentiation via STAC core property: `properties.platform ∈ {"LANDSAT_8", "LANDSAT_9"}`

### Search Authentication

- **Required:** No. Provider catalog, `/collections`, `/search`, and item endpoints respond anonymously.
- **Implication:** `create_usgs_landsat_catalog()` calls `pystac_client.Client.open(USGS_LANDSAT_API)` with the standard retry wrapper. No auth header on the catalog client.

### Asset Access

**USGS EROS M2M Protocol:** Asset hrefs point to USGS infrastructure (`landsatlook.usgs.gov`) which requires USGS EROS Machine-to-Machine (M2M) authentication.

We will implement the M2M protocol using the `USGS_USERNAME` and `USGS_TOKEN` environment variables.

1. Issue an anonymous `Landsat8Search` for a small bbox + recent date range against `landsatlook.usgs.gov/stac-server`.
2. Authenticate using M2M: POST to `https://m2m.cr.usgs.gov/api/api/json/stable/login-token` with the credentials to get a session token, and use the returned token as the `X-Auth-Token` header for requests.

### Asset Download — Required Behaviors (regardless of auth host)

- **Headless Safety:** If credentials missing, prompt only when `sys.stdin.isatty()` is true; otherwise raise `ValueError`/`RuntimeError` to fail fast in CI.
- **Memory Safety:** `stream=True` with chunked writes (e.g. 8 MiB blocks) — Landsat scenes are multi-GB.
- **Atomic Writes:** Stream to `<final_path>.partial`, rename only on success. All paths via `pathlib.Path`.
- **Content-Type Validation:** Assert response final `Content-Type` is not `text/html`. Call `raise_for_status()`. This must run **before** any bytes are written.
- **Refactor scope:** `src/geospatial_tools/utils.py:download_url` (line ~177) currently uses `response.content` (full body in RAM, no streaming, no content-type check) — **fix this function**, not just add a new branch. Then the UsgsLandsat branch only adds session/auth on top.

## 3. 🛡️ Verification & Failure Modes (FMEA)

- **Pre-implementation gating:** Asset href reconnaissance (see §2.1). Block all auth code until host confirmed.
- **Test Strategy:**
    - Register `integration` and `online` pytest markers in `pyproject.toml` (pre-existing tech debt — current tests use them but they are unregistered, triggering `PytestUnknownMarkWarning`).
    - Unit tests for STAC core wiring (mock `pystac_client.Client.open`).
    - Unit tests for `UsgsLandsatLandsatCollection` / `UsgsLandsatLandsatProperty` / `UsgsLandsatLandsatBand` enum values.
    - Unit tests for `AbstractLandsat` query construction (assert platform filter present without network).
    - Unit tests for auth handling: TTY check, missing credentials in headless mode, HTML response rejection.
    - Integration tests (`@pytest.mark.integration`) for real CMR USGS_EROS searches (no asset bytes).
    - Online tests (`@pytest.mark.online`) for credentialed download path; skip cleanly when env vars missing.
- **Data Integrity:** Chunked atomic streaming writes (`.partial`). Validate downloaded file opens via `rasterio` as `GTiff`.
- **Auth Failures:** Raise explicit exceptions on 401/403, on `Content-Type: text/html`, and on missing credentials in headless mode. Never swallow exceptions.

## 4. 📋 Granular Implementation Steps

| Step | Description                                                                                                                            | Task File   |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| 0    | **Prerequisites:** register pytest markers, add `requests` as explicit dependency.                                                     | `TASK-0.md` |
| 1    | **Core STAC wiring:** add `USGS_LANDSAT` catalog (USGS_EROS provider URL), `create_usgs_landsat_catalog`, dispatch entry, retry tests. | `TASK-1.md` |
| 2    | **Constants:** pin collection ID, properties, bands (after one-time CMR item inspection).                                              | `TASK-2.md` |
| 3    | **Refactor `AbstractStacWrapper`** to accept `catalog_name`; implement `AbstractLandsat`.                                              | `TASK-3.md` |
| 4    | **Concrete classes:** `Landsat8Search`, `Landsat9Search`. Hardcode `platform` property filter.                                         | `TASK-4.md` |
| 5    | **Integration tests** (live CMR search, no downloads).                                                                                 | `TASK-5.md` |
| 6    | **Asset href reconnaissance + auth + safe `_download_assets` branch.** Refactor `utils.download_url` for streaming/safety.             | `TASK-6.md` |
| 7    | **Online tests:** credentialed download verification, GeoTIFF integrity check.                                                         | `TASK-7.md` |
| —    | **Validation:** every task ends with `make precommit && make pylint && make test && make mypy`.                                        | per task    |
| —    | **Init export:** included as TASK-4 subtask 4 (`src/geospatial_tools/stac/usgs_landsat/__init__.py`).                                  | TASK-4      |

```
                    | TASK-4      |
```
