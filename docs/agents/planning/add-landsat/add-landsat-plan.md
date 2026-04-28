# Formal Design Document — Add Landsat 8 & 9 (USGS STAC)

## 1. 🎯 Scope & Context

Add support for downloading Landsat 8 and Landsat 9 Top of Atmosphere (Level-1) imagery.
The goal is to provide a fluent builder interface for Landsat data, matching the pattern established in `AbstractStacWrapper`.
Since Planetary Computer only provides Level-2 (Surface Reflectance) for Landsat 8/9, we must integrate a new STAC catalog source: the USGS STAC Catalog (`https://landsatlook.usgs.gov/stac-server`), which provides the `landsat-c2l1` collection for Level-1 data.

## 2. 🧠 Architectural Approach (Trade-offs & Strategy)

- **New STAC Catalog Integration:** Add the USGS STAC catalog to the core STAC module (`src/geospatial_tools/stac/core.py`) alongside `planetary_computer` and `copernicus`.
- **Facade + Proxy Pattern:** Inherit `Landsat8Search` and `Landsat9Search` from `AbstractStacWrapper`, pointing them to the new USGS catalog instead of Planetary Computer.
- **Unified Base Class:** Create an `AbstractLandsat` base class to avoid code duplication since Landsat 8 and 9 bands and STAC properties are identical. `Landsat8Search` and `Landsat9Search` will inherit from it and hardcode their respective platforms (`LANDSAT_8` and `LANDSAT_9`).
- **Explicit Enum Constants:** Add `UsgsLandsatCollection`, `UsgsLandsatProperty`, and `UsgsLandsatBand` to `src/geospatial_tools/stac/usgs/constants.py` to maintain strong typing.
- **Trade-off - Multiple Catalogs:** Introducing a new catalog increases testing surface and potential points of failure (e.g., rate limits on USGS servers vs. Microsoft's), but it is strictly required to get Level-1 data.

## 2.1 🌐 USGS STAC Catalog Specifications

This subsection records the verified properties of the USGS STAC API as of 2026-04-27 so that downstream design decisions (auth, download path, dispatcher wiring) rest on confirmed facts rather than assumptions.

### Endpoint & Protocol

- **Root URL:** `https://landsatlook.usgs.gov/stac-server` (verified — returns a valid STAC API root).
- **STAC version:** 1.1.0.
- **Conformance:** STAC core, collections, item-search, OGC API Features 1.0, CQL2 filtering.
- **Search endpoints:** `GET`/`POST https://landsatlook.usgs.gov/stac-server/search`.
- **Collection endpoint:** `https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l1`.
- **Provider:** USGS EROS Center (`producer`, `processor`, `host`).
- **License:** Open (Landsat Data Policy).

### Search Authentication

- **Required:** No. The root, `/collections`, `/search`, and item endpoints respond anonymously.
- **Implication:** `create_usgs_catalog()` only needs `pystac_client.Client.open(USGS_API)` plus the same retry wrapper used by `create_planetary_computer_catalog()`. **No `usgs/auth.py` module is required for v1**, in contrast with `copernicus/auth.py` (which exists because Copernicus requires OIDC password-grant tokens).

### Asset Access — Two Hrefs Per Asset

Each STAC item asset exposes both:

1. **Primary `href`:** `https://landsatlook.usgs.gov/data/...` — direct, anonymous HTTPS GET. No token, no signing, no redirect to a login wall.
2. **Alternate `alternate.s3.href`:** `s3://usgs-landsat/...` with `storage:platform: "AWS"` and `storage:requester_pays: true`.

**v1 download strategy:** use the primary HTTPS href. The existing `StacSearch._download_assets` default branch (`method = "http"`, no headers) at `src/geospatial_tools/stac/core.py:730` is sufficient. **No new auth branch needs to be added** for USGS.

**Out of scope for v1:** the S3 alternate path. Using it would require AWS credentials in the caller's environment, the `--request-payer requester` flag (caller pays egress), and a new requester-pays branch in `_download_assets`. Document as a future-work note; do not implement.

### Catalog-Generator Wiring (resolves prior review point)

`catalog_generator()` at `src/geospatial_tools/stac/core.py:109` uses an explicit dispatch dict. Step 1 of Section 4 must extend it as follows; failure to wire it leaves `StacSearch(USGS)` returning `None` and breaks every Landsat search silently:

```python
catalog_dict = {
    PLANETARY_COMPUTER: create_planetary_computer_catalog,
    COPERNICUS: create_copernicus_catalog,
    USGS: create_usgs_catalog,  # new
}
```

Also extend `CATALOG_NAME_LIST` to include `USGS` so `list_available_catalogs()` reports it.

### Download-Path Integration (resolves prior review point)

- **Default branch (`method = "http"`):** works as-is for USGS HTTPS hrefs. No code change required in `_download_assets`.
- **Verification gate:** the online test in Step 6 must download at least one band via the default branch and assert the file is non-empty and a valid GeoTIFF. This is the only way to catch a silent regression if USGS later moves to signed URLs.
- **No headers, no `s3_client`, no token** are required for v1. `self.s3_client` remains `None` for `StacSearch(USGS)` (matches the Planetary Computer initialization).

### Rate Limits & Reliability

- **Documented limits:** none published by USGS for the STAC server. Treat as best-effort.
- **Mitigation:** reuse the existing retry/backoff wrapper from `create_planetary_computer_catalog()` for `create_usgs_catalog()`. Same `max_retries` / `delay` parameters.
- **CI policy:** Live-network tests against the USGS endpoint must be excluded from default `make test` runs to avoid CI flakiness from network or rate-limit spikes. Two distinct markers apply:
    - `@pytest.mark.integration` — tests that exercise real STAC search results without patching `StacSearch`. Metadata only; **no asset bytes downloaded**.
    - `@pytest.mark.online` — tests that actually pull asset bytes over the network (the download verification gate in Step 6).

## 3. 🛡️ Verification & Failure Modes (FMEA)

- **Validation Gates:**
    - Code must pass `make precommit`, `make pylint`, `make test`, and `make mypy`.
- **Test Strategy:**
    - Unit tests for catalog creation in `test_stac_core.py`.
    - Unit tests for query construction in `test_usgs_landsat.py` to ensure `platform` filters are injected correctly. Mock at the `pystac_client`/HTTP boundary, **not** `StacSearch` itself — that is the seam exercised by the integration tier.
    - Integration tests (`@pytest.mark.integration`) in `test_usgs_landsat_integration.py` exercising real USGS STAC searches without patching `StacSearch`; verify `platform` and asset-key contracts on the returned items. No asset bytes downloaded.
    - Online tests (`@pytest.mark.online`) in `test_usgs_landsat_online.py` covering the end-to-end download path (anonymous-HTTPS regression gate).
- **Known Risks:**
    - **USGS API Rate Limits:** No documented limits. The `create_usgs_catalog` retry logic must handle transient timeouts and 5xx responses gracefully (reuse the existing retry pattern).
    - **Asset Auth (resolved):** Verified — the primary HTTPS hrefs returned by the USGS STAC are anonymously downloadable. No EarthExplorer / EROS token is required for the v1 download path. Risk is residual: if USGS migrates assets behind signed URLs in future, the online test in Step 6 must catch the regression.
    - **S3 Requester-Pays (out of scope):** The `alternate.s3.href` URIs are flagged `storage:requester_pays: true`. Using them would charge the caller's AWS account for egress. Not implemented in v1; if added later, requires a new branch in `StacSearch._download_assets` analogous to the Copernicus S3 branch but with the `RequestPayer="requester"` flag.
    - **Data Volume:** Landsat L1 scenes are large. We must ensure the proxy pattern doesn't eagerly download without explicit `download()` calls.

## 4. 📋 Granular Implementation Steps

1. **Add USGS Catalog Core Logic** — Modify `src/geospatial_tools/stac/core.py` to:
    - Add `USGS = "usgs"` constant and `USGS_API = "https://landsatlook.usgs.gov/stac-server"` constant.
    - Extend `CATALOG_NAME_LIST` to include `USGS`.
    - Implement `create_usgs_catalog(max_retries, delay, logger)` reusing the retry/backoff pattern from `create_planetary_computer_catalog()`. No auth module is needed (verified — see Section 2.1).
    - **Register the factory in `catalog_generator()`'s dispatch dict** at `core.py:109` (`USGS: create_usgs_catalog`). Without this, `StacSearch(USGS)` returns `None` and Landsat searches fail silently.
    - Confirm `StacSearch._download_assets` (`core.py:730`) requires no new branch: USGS hrefs flow through the default `method = "http"` path. The online test in Step 6 is the gate that proves this end-to-end.
2. **Create constants** — Add `UsgsLandsatCollection`, `UsgsLandsatProperty`, and `UsgsLandsatBand` to `src/geospatial_tools/stac/usgs/constants.py`.
3. **Create Landsat module** — Add `src/geospatial_tools/stac/usgs/landsat.py` with an `AbstractLandsat` base class inheriting from `AbstractStacWrapper` (using the USGS catalog).
4. **Implement concrete classes** — Add `Landsat8Search` and `Landsat9Search` that hardcode the `platform` query to `LANDSAT_8` and `LANDSAT_9`.
5. **Write unit + integration tests** — Create `tests/test_usgs_landsat.py` for unit tests (mock the `pystac_client`/HTTP boundary; never patch `StacSearch`) covering query building and platform filtering. Create `tests/test_usgs_landsat_integration.py` (`@pytest.mark.integration`) exercising real USGS STAC searches without patching `StacSearch`, asserting `platform` and asset-key contracts. No asset bytes downloaded here.
6. **Write online download tests** — Create `tests/test_usgs_landsat_online.py` (`@pytest.mark.online`) with the download verification gate: pull one small band asset via the default `method = "http"` branch of `_download_assets`, validate as a non-empty GeoTIFF.
7. **Update `__init__.py`** — Expose the new Landsat classes in `src/geospatial_tools/stac/usgs/__init__.py`.
8. **Run validation gates** — Run `make precommit`, `make pylint`, `make test`, and `make mypy`.

## 5. ⏭️ Next Step

> Shall I proceed with Step 1 — Add USGS Catalog Core Logic to `stac/core.py`?
