# Formal Design Document — Add Landsat 8 & 9 (NASA Earthdata STAC)

## 1. 🎯 Scope & Context

Add support for downloading Landsat 8 and 9 Top of Atmosphere (Level-1) imagery.
Provide fluent builder interface for Landsat data. Match `AbstractStacWrapper` pattern.
Planetary Computer only provides Level-2 (Surface Reflectance) for Landsat 8/9. Use NASA Earthdata STAC Catalog (`https://cmr.earthdata.nasa.gov/stac/`).

## 2. 🧠 Architectural Approach (Trade-offs & Strategy)

- **New STAC Catalog:** Add Earthdata STAC catalog to `src/geospatial_tools/stac/core.py`.
- **Facade + Proxy Pattern:** Inherit `Landsat8Search` and `Landsat9Search` from `AbstractStacWrapper`. Point to Earthdata catalog.
- **Unified Base Class:** Create `AbstractLandsat` base class to avoid duplication.
- **Explicit Enum Constants:** Add `EarthdataLandsatCollection`, `EarthdataLandsatProperty`, and `EarthdataLandsatBand` to `src/geospatial_tools/stac/earthdata/constants.py`.

## 2.1 🌐 NASA Earthdata STAC Catalog Specs

### Endpoint & Protocol

- **Root URL:** `https://cmr.earthdata.nasa.gov/stac/`
- **Search endpoints:** `GET`/`POST https://cmr.earthdata.nasa.gov/stac/search`

### Search Authentication

- **Required:** No. Root, `/collections`, `/search`, and item endpoints respond anonymously.
- **Implication:** `create_earthdata_catalog()` needs `pystac_client.Client.open(EARTHDATA_API)` + retry wrapper. No auth header on catalog client.

### Asset Access

- **Primary `href`:** HTTPS links require NASA Earthdata Login (EDL) authentication.
- **Required:** New `src/geospatial_tools/stac/earthdata/auth.py` for EDL credentials (`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`).
- **Download Branch:** New auth branch in `StacSearch._download_assets`. Must follow EDL redirects. Use streaming atomic writes (`.partial` suffix) to prevent corrupted files.
- **Content-Type Validation:** Must assert response `Content-Type` is not `text/html`. Prevent writing login HTML as asset.

## 3. 🛡️ Verification & Failure Modes (FMEA)

- **Test Strategy:**
    - Unit tests for STAC core logic.
    - Unit tests for query construction.
    - Unit tests for auth handling and EDL redirects.
    - Integration tests (`@pytest.mark.integration`) for real STAC searches.
    - Online tests (`@pytest.mark.online`) verifying credentialed download path.
- **Data Integrity:** Use atomic streaming writes (`.partial`). Validate file opens via `rasterio` after download.
- **Auth Failures:** Raise explicit exceptions if EDL login fails or redirects to HTML.

## 4. 📋 Granular Implementation Steps

1. **Core STAC:** Add Earthdata catalog logic in `src/geospatial_tools/stac/core.py`.
2. **Constants:** Add Enums to `src/geospatial_tools/stac/earthdata/constants.py`.
3. **Landsat Module:** Add `AbstractLandsat` in `src/geospatial_tools/stac/earthdata/landsat.py`.
4. **Concrete Classes:** Implement `Landsat8Search` and `Landsat9Search`.
5. **Integration Tests:** Create `tests/test_earthdata_landsat_integration.py`.
6. **Earthdata Auth & Download:** Implement `auth.py` and Earthdata branch in `_download_assets`. Add `.partial` atomic writes and HTML validation.
7. **Online Tests:** Create `tests/test_earthdata_landsat_online.py` to test EDL download flow.
8. **Init:** Expose classes in `src/geospatial_tools/stac/earthdata/__init__.py`.
9. **Validation:** Run `make precommit`, `make pylint`, `make test`, and `make mypy`.
