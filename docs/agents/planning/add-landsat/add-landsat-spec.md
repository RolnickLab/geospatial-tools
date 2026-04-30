# SPEC: Add Earthdata STAC Landsat 8 & 9 (Level-1 TOA) Support

## 1. Overview

- **Goal:** Add fluent builder interface (`Landsat8Search` and `Landsat9Search`) to query and download Landsat 8 and 9 Top of Atmosphere (Level-1) imagery.
- **Problem Statement:** Planetary Computer lacks Landsat 8/9 Level-1 (TOA) data. Must integrate NASA Earthdata STAC catalog and provide search classes mirroring `AbstractStacWrapper` pattern.

## 2. Requirements

### Functional Requirements

- Add Earthdata STAC Catalog endpoint (`https://cmr.earthdata.nasa.gov/stac/`) to `src/geospatial_tools/stac/core.py`.
- Implement `create_earthdata_catalog()` in `stac/core.py` with retry logic. Catalog client is anonymous.
- Define Enums for Earthdata Landsat collections, properties, and bands in `src/geospatial_tools/stac/earthdata/constants.py`.
- Implement `AbstractLandsat` base class inheriting from `AbstractStacWrapper`.
- Implement `Landsat8Search` and `Landsat9Search` classes hardcoding respective platform parameters (`LANDSAT_8`, `LANDSAT_9`).
- Implement `src/geospatial_tools/stac/earthdata/auth.py`. Resolve NASA Earthdata Login credentials from env (`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`) with interactive prompt fallback. Handle EDL redirects.
- Add Earthdata branch in `StacSearch._download_assets`. Inject Earthdata credential and assert response `Content-Type` is not `text/html` before writing bytes. Prevent silently writing login HTML.
- Expose new classes in `src/geospatial_tools/stac/earthdata/__init__.py`.

### Non-Functional Requirements

- **Reliability:** Handle network timeouts gracefully via retry loops.
- **Data Integrity:** Use atomic streaming writes (`.partial` suffix) and content-type validation.
- **Code Quality:** Adhere strictly to project formatting, typing, and linting standards.

## 3. Technical Constraints & Assumptions

- **Design Pattern:** Must implement Facade + Proxy pattern defined by `AbstractStacWrapper`.
- **Catalog Wiring:** `catalog_generator()` must register `EARTHDATA: create_earthdata_catalog` in dispatch dict.
- **Search Authentication:** Earthdata STAC API responds anonymously.
- **Asset Download Authentication:** Primary HTTPS download links require NASA Earthdata Login (EDL). Unauthenticated requests redirect to HTML login page.
- **Content-Type Validation:** Earthdata download branch must assert response `Content-Type` is not `text/html` before writing bytes.

## 4. Acceptance Criteria

- `stac.core.list_available_catalogs()` returns set including `"earthdata"`.
- `Landsat8Search().search()` and `Landsat9Search().search()` construct STAC queries and return results.
- `earthdata/auth.py` resolves credentials from env or prompt. Raises clear error when missing.
- `StacSearch._download_assets` Earthdata branch downloads sample band. Refuses response if `Content-Type` is `text/html`. Atomic writes using `.partial`.
- `make precommit`, `make pylint`, `make test`, and `make mypy` run without errors.

## 5. Dependencies

- Internal: `AbstractStacWrapper`, `StacSearch` from `src/geospatial_tools/stac/core.py`.
- External: `pystac_client` communicating with `https://cmr.earthdata.nasa.gov/stac/`.

## 6. Out of Scope

- Support for Landsat Level-2 (Surface Reflectance) data on Planetary Computer.
- Support for Landsat 1-7.
- Direct S3 access.

## 7. Verification Plan

- **Unit Tests:** Verify `create_earthdata_catalog` retry logic, `AbstractLandsat` query construction, and `auth.py` HTML response handling.
- **Integration Tests:** Execute live search against Earthdata STAC API (`@pytest.mark.integration`). No asset bytes downloaded.
- **Online Tests:** Trigger download via Earthdata branch (`@pytest.mark.online`). Assert flow acquires file correctly and opens with `rasterio` as `GTiff`.
