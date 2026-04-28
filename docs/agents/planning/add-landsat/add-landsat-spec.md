# SPEC: Add USGS STAC Landsat 8 & 9 (Level-1 TOA) Support

## 1. Overview

- **Goal**: Add a fluent builder interface (`Landsat8Search` and `Landsat9Search`) to query and download Landsat 8 and 9 Top of Atmosphere (Level-1) imagery.
- **Problem Statement**: Existing Planetary Computer wrappers only support Sentinel data. Landsat 8 and 9 Level-1 (TOA) data is not available on Planetary Computer (only Level-2 is). To support Landsat 8/9 L1, we must integrate the USGS STAC catalog and provide search classes that mirror the existing `AbstractStacWrapper` pattern.

## 2. Requirements

### Functional Requirements

- [ ] Add the USGS STAC Catalog endpoint (`https://landsatlook.usgs.gov/stac-server`) to `src/geospatial_tools/stac/core.py`.
- [ ] Implement `create_usgs_catalog()` in `stac/core.py` with retry logic.
- [ ] Define Enums for USGS Landsat collections, properties, and bands in `src/geospatial_tools/stac/usgs/constants.py`.
- [ ] Implement an `AbstractLandsat` base class inheriting from `AbstractStacWrapper`.
- [ ] Implement `Landsat8Search` and `Landsat9Search` classes that hardcode their respective `platform` query parameters (`LANDSAT_8` and `LANDSAT_9`).
- [ ] Expose the new classes in `src/geospatial_tools/stac/usgs/__init__.py`.

### Non-Functional Requirements

- **Reliability**: The USGS catalog creation must handle network timeouts gracefully via retry loops (matching existing `planetary_computer` logic).
- **Code Quality**: All new code must strictly adhere to project formatting, typing, and linting standards.

## 3. Technical Constraints & Assumptions

- **Constraint - Data Source**: Must use the `landsat-c2l1` collection on the USGS STAC.
- **Constraint - Design Pattern**: Must implement the Facade + Proxy pattern defined by `AbstractStacWrapper`.
- **Constraint - Catalog Wiring**: `catalog_generator()` in `stac/core.py` must register `USGS: create_usgs_catalog` in its dispatch dict; otherwise `StacSearch(USGS)` returns `None` and Landsat searches fail silently.
- **Verified - Authentication**: The USGS STAC API root, `/collections`, `/search`, and item endpoints respond anonymously (verified 2026-04-27). Primary asset hrefs (`https://landsatlook.usgs.gov/data/...`) are direct, anonymous HTTPS GETs — no token, no signing, no redirect. **No `usgs/auth.py` module is required for v1**, in contrast with `copernicus/auth.py`.
- **Verified - Download Path**: USGS hrefs flow through the existing default branch (`method = "http"`) of `StacSearch._download_assets`. No new auth branch is required for v1.
- **Assumption - Stability**: The verified anonymous-HTTPS contract is assumed stable for the v1 release. The integration test in §7 is the regression gate if USGS later moves assets behind signed URLs.

## 4. Acceptance Criteria

- [ ] `stac.core.list_available_catalogs()` returns a set including `"usgs"`.
- [ ] `Landsat8Search().search()` constructs a STAC query with `{"platform": {"eq": "LANDSAT_8"}}` and returns results.
- [ ] `Landsat9Search().search()` constructs a STAC query with `{"platform": {"eq": "LANDSAT_9"}}` and returns results.
- [ ] `make precommit`, `make pylint`, `make test`, and `make mypy` run without errors.

## 5. Dependencies

- Internal: `AbstractStacWrapper`, `StacSearch` from `src/geospatial_tools/stac/core.py`.
- External: `pystac_client` communicating with `https://landsatlook.usgs.gov/stac-server`.

## 6. Out of Scope

- **EarthExplorer/EROS authentication flows.** Verified unnecessary for v1 — primary STAC asset hrefs are anonymous HTTPS GETs. If USGS later moves assets behind signed URLs, the v1 integration test (§7) is the regression gate.
- **S3 alternate path (`alternate.s3.href`).** Each asset exposes a secondary S3 href flagged `storage:requester_pays: true`. Using it would require AWS credentials in the caller's environment, the `--request-payer requester` flag (caller pays egress), and a new requester-pays branch in `StacSearch._download_assets` analogous to the Copernicus S3 branch but with `RequestPayer="requester"`. Not implemented in v1.
- Support for Landsat Level-2 (Surface Reflectance) data on Planetary Computer.
- Support for Landsat 1-7.

## 7. Verification Plan

- **Unit Tests**:
    - Verify `create_usgs_catalog` initialization and retry logic in `test_stac_core.py`.
    - Verify `catalog_generator(USGS)` returns a configured client (dispatch-dict wiring).
    - Verify `AbstractLandsat` subclass query construction (specifically `platform` filters) in `test_usgs_landsat.py` using mocking. Mock at the `pystac_client`/HTTP layer; **do not** patch `StacSearch` itself — the integration tier exercises that boundary.
- **Integration Tests** (must be marked `@pytest.mark.integration` and excluded from default `make test` runs; live STAC search, **no asset bytes downloaded**):
    - In `tests/test_usgs_landsat_integration.py`, execute a live search against the USGS STAC API for Landsat 8 and Landsat 9 without patching `StacSearch`; assert results are non-empty and that `item.properties["platform"]` matches `LANDSAT_8` / `LANDSAT_9`.
    - Assert expected Level-1 TOA asset keys (e.g. `coastal`, `blue`, `red`, `nir08`, `qa_pixel`) resolve in `item.assets`.
- **Online Tests** (must be marked `@pytest.mark.online` and excluded from default `make test` runs; pulls real bytes over the network):
    - In `tests/test_usgs_landsat_online.py`, **download verification gate**: download at least one small band asset via the default `method = "http"` branch of `_download_assets` and assert the file is non-empty and a valid GeoTIFF. This is the regression gate for the anonymous-HTTPS contract; without it, a USGS migration to signed URLs would silently break the download path.
- **Validation Gates**:
    - Run the project's standard `make` targets (`precommit`, `pylint`, `test`, `mypy`) to enforce architectural and stylistic requirements.
