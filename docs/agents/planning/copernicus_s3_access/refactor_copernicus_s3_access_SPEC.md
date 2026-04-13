# SPEC: Refactor Copernicus Data Access to S3 Protocol

## 1. Overview

- **Goal**: Switch the Copernicus Sentinel-2 STAC asset download mechanism from HTTP(S) via the `requests` library to direct S3 access using `boto3`.
- **Problem Statement**: Currently, `geospatial_tools.stac` downloads Copernicus Sentinel-2 data using HTTP links from STAC assets (`href`). These redirect to S3 buckets. Bypassing the HTTP layer and using direct `boto3` S3 access is more robust, efficient, and aligns with standard cloud-native geospatial workflows (Clean Architecture / System Design).

## 2. Requirements

### Functional Requirements

- [ ] Add `boto3` as a project dependency.
- [ ] Implement an S3 credential management strategy loading `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `COPERNICUS_S3_ENDPOINT` via `python-dotenv` from a `.env` file.
- [ ] Create a dedicated module (`geospatial_tools.s3_utils`) responsible for instantiating the `boto3` client with the correct endpoint URL and parsing STAC `href` values into bucket/key combinations.
- [ ] Refactor the `StacSearch._download_assets` method in `stac.py` to use a strategy pattern or dispatcher: handling "s3" methods via the new `s3_utils` module, and falling back to the existing "http" method via `requests` for other catalogs.
- [ ] Update local configuration templates (`.env.example`) with the required S3 environment variables.

### Non-Functional Requirements

- **Reliability & Idempotency (Python Skill)**: S3 downloads must handle network failures gracefully, using `boto3`'s built-in retries.
- **Evolvability & Decoupling (System Design Skill)**: The download logic must be strictly decoupled from the STAC search logic.
- **Backward Compatibility**: The existing HTTP download capabilities must remain intact to support other STAC catalogs (e.g., Planetary Computer) that do not use S3 directly.

## 3. Technical Constraints & Assumptions

- **Dependencies**: The system depends on `boto3` for S3 interaction and `python-dotenv` (already present) for environment variable management.
- **Assumptions**: The `href` from the CDSE STAC items points to or can be deterministically resolved to a valid S3 bucket and key accessible via the Copernicus S3 endpoint. Standard AWS environment variables will be recognized by the underlying `boto3` session.
- **Coding Standards**: Strict adherence to project standards: `pathlib.Path` for filesystem operations, type hints, and `structlog` for logging instead of `print()`.

## 4. Acceptance Criteria

- [ ] `boto3` is successfully added to `pyproject.toml`.
- [ ] `.env.example` includes `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `COPERNICUS_S3_ENDPOINT` variables.
- [ ] `geospatial_tools.s3_utils.py` provides working functions to get a configured S3 client and parse S3 URIs.
- [ ] `geospatial_tools.stac` routes downloads for Copernicus data through the new `boto3` integration without breaking the HTTP path for other data sources.
- [ ] Unit tests are added/updated to verify the dispatcher logic and S3 URL parsing (using mocked S3 clients where necessary).
- [ ] Integration test (`test_copernicus.py`, marked `@pytest.mark.online`) successfully downloads a real STAC asset using S3.

## 5. Dependencies

- `boto3` (New dependency to be added to `pyproject.toml`)
- Existing `pytest` suite for verification.
- Valid CDSE S3 credentials for local/CI integration testing.

## 6. Out of Scope

- Modifying the underlying search logic in `pystac-client`.
- Refactoring the HTTP download method (`requests`) for performance, unless necessary to fit the new dispatcher pattern.
- Handling S3 multi-part uploads or operations other than basic GET/download.

## 7. Verification Plan (Orchestrator Skill)

The implementation will be verified through a combination of mocked unit tests and an end-to-end online test:

1. **Unit Verification**: Run `pytest tests/` ensuring any new S3-specific unit tests (with mocked `boto3` clients) verify URL parsing and correct dispatcher behavior in `stac.py`.
2. **Integration Verification**: With a properly configured `.env` file containing valid CDSE S3 credentials, execute `pytest tests/test_copernicus.py -m online`. This end-to-end test serves as the ultimate proof that the entire chain—STAC search, asset extraction, S3 client configuration, and binary download—functions correctly against the live Copernicus Data Space Ecosystem.
