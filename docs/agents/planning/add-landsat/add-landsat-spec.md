# SPEC: Add CMR STAC (USGS_EROS) Landsat 8 & 9 Level-1 Support

## 1. Overview

- **Goal:** Add fluent builder interface (`Landsat8Search`, `Landsat9Search`) to query and download Landsat 8/9 **Level-1 Collection 2** imagery (calibrated digital numbers; TOA reflectance computation is downstream and out of scope).
- **Problem Statement:** Planetary Computer lacks Landsat 8/9 Level-1. Use NASA CMR STAC, **provider `USGS_EROS`**, and provide search classes mirroring the `AbstractStacWrapper` pattern.
- **Hard constraint:** UsgsLandsat (CMR) STAC catalog. Do not switch.

## 2. Requirements

### Functional Requirements

- Add CMR `USGS_EROS`-scoped STAC endpoint (`https://landsatlook.usgs.gov/stac-server`) to `src/geospatial_tools/stac/core.py`. The bare `/stac/` root is the provider list, not a usable search endpoint.
- Implement `create_usgs_landsat_catalog()` in `core.py` reusing the retry pattern. Catalog client is anonymous.
- Define enums for the single shared L1 collection, platform property, and asset/band keys in `src/geospatial_tools/stac/usgs_landsat/constants.py`. Collection ID (verified): `"landsat-c2l1"`.
- **Refactor `AbstractStacWrapper.__init__`** (`core.py:904`) to accept `catalog_name: str = PLANETARY_COMPUTER`. Backward-compatible default for Sentinel-1/2/3 wrappers; Landsat passes `USGS_LANDSAT`.
- **Refactor `StacSearch.__init__`** (`core.py:432-433`) so that the S3 client is initialized only when explicitly relevant (currently fires for `COPERNICUS`). Adding a new catalog must not change S3 wiring semantics.
- Implement `AbstractLandsat(AbstractStacWrapper)` and concrete `Landsat8Search`, `Landsat9Search` classes. Both target the same collection ID; `_build_collection_query()` injects `{"platform": {"eq": "LANDSAT_8"|"LANDSAT_9"}}`.
- Implement `src/geospatial_tools/stac/usgs_landsat/auth.py`. Resolve credentials from env (variable names pinned by the asset-host verification step in TASK-6). Prompt only when `sys.stdin.isatty()` is true; otherwise fail fast.
- **Refactor** `src/geospatial_tools/utils.py:download_url` to: stream (`stream=True`), chunked write (~8 MiB blocks), `.partial` suffix + rename, `raise_for_status()`, content-type guard rejecting `text/html`. This is a safety upgrade for ALL callers, not just UsgsLandsat.
- **Extend `download_stac_asset` dispatcher** (`core.py:379-408`) with a third method: `method = "usgs_landsat"`. Accepts a `requests.Session` (or `SessionWithHeaderRedirection` subclass) instead of plain headers; routes to a session-aware streaming download.
- Add an UsgsLandsat branch in `StacSearch._download_assets` (`core.py:713-761`) that constructs the auth session and dispatches via `method="usgs_landsat"`.
- Expose new classes in `src/geospatial_tools/stac/usgs_landsat/__init__.py`.
- **Register pytest markers** `integration` and `online` in `pyproject.toml` `[tool.pytest.ini_options]`.

### Non-Functional Requirements

- **Reliability:** Network retries on STAC client open. `raise_for_status()` on every download HTTP call.
- **Data Integrity:** Streamed chunked atomic writes via `pathlib.Path` and `.partial` suffix. Verify opened raster is a valid `GTiff` via `rasterio` in online tests.
- **Memory Safety:** Multi-GB scenes must never load into RAM in full.
- **Code Quality:** stdlib `logging` (consistent with existing `core.py`/`utils.py`). `pathlib.Path` exclusively. Explicit keyword arguments.

## 3. Technical Constraints & Assumptions

- **Design Pattern:** Facade + Proxy via `AbstractStacWrapper`.
- **Catalog Wiring:** `catalog_generator()` registers `USGS_LANDSAT: create_usgs_landsat_catalog`.
- **Search Authentication:** CMR STAC responds anonymously.
- **Asset Download Authentication:** Use USGS EROS auth (M2M token via POST to `https://m2m.cr.usgs.gov/api/api/json/stable/login-token`, then `X-Auth-Token` header).
    - Env-var names are `USGS_USERNAME` and `USGS_TOKEN`.
- **Content-Type Validation:** Both the refactored `download_url` and the new `usgs_landsat` branch must reject `text/html` responses before writing bytes. Past incident: naive GET against `landsatlook.usgs.gov` writes the login HTML to disk with status 200 (memory note `usgs_landsat_auth.md`).

## 4. Acceptance Criteria

- `stac.core.list_available_catalogs()` returns set including `"usgs_landsat"`.
- `Landsat8Search().search()` and `Landsat9Search().search()` return real items from CMR `USGS_EROS`. Items have `properties.platform` matching the requested platform string.
- `usgs_landsat/auth.py` resolves credentials from env or interactive prompt (only when TTY). Raises clear error in headless mode without credentials.
- `StacSearch._download_assets` UsgsLandsat branch downloads a sample band as a real GeoTIFF. Refuses to write if response `Content-Type` is `text/html`. Atomic chunked writes via `.partial` and `pathlib.Path`.
- Refactored `download_url` no longer loads full body to memory and rejects HTML responses.
- `pyproject.toml` declares `integration` and `online` pytest markers.
- `make precommit`, `make pylint`, `make test`, and `make mypy` run clean.

## 5. Dependencies

- **Internal:** `AbstractStacWrapper`, `StacSearch` from `src/geospatial_tools/stac/core.py`.
- **External:**
    - `pystac_client` against `https://landsatlook.usgs.gov/stac-server`.
    - `requests` — currently a transitive dependency only (via `boto3`); add as explicit dependency in `pyproject.toml`.

## 6. Out of Scope

- Landsat Level-2 (Surface Reflectance / Surface Temperature) on Planetary Computer or CMR.
- Landsat 1-7.
- Direct S3 access (USGS Requester-Pays bucket, etc.).
- Pre-computed TOA reflectance products (TOA must be derived from L1 + MTL.txt downstream of this feature).
- Migration of existing modules from stdlib `logging` to `structlog`.

## 7. Verification Plan

- **Authentication Implementation:** Implement USGS EROS M2M authentication for asset download.
- **Unit Tests:**
    - `create_usgs_landsat_catalog` retry behavior (mock `pystac_client.Client.open`).
    - `UsgsLandsatLandsat*` enum values.
    - `AbstractLandsat`/`Landsat8Search`/`Landsat9Search` query construction (no network).
    - `auth.py`: missing-credentials-in-headless raises, TTY-prompt only when interactive, HTML-response rejection.
    - Refactored `download_url`: streaming, atomic rename, HTML rejection.
- **Integration Tests** (`@pytest.mark.integration`): live CMR USGS_EROS search; no asset bytes.
- **Online Tests** (`@pytest.mark.online`): full credentialed download via `_download_assets` UsgsLandsat branch; assert atomic `.partial` rename and `rasterio.open(...)` succeeds with `driver == "GTiff"`. Skip cleanly when env vars unset.
