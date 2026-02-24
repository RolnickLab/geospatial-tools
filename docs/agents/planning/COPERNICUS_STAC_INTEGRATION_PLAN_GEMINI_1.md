# Copernicus STAC Catalog Integration Plan

## 1. Objective

Integrate the Copernicus Data Space Ecosystem (CDSE) STAC catalog into the `geospatial_tools` library, enabling users to search and download Sentinel data (and other Copernicus products) alongside the existing Planetary Computer integration.

## 2. Analysis & Requirements

### 2.1. Target API

- **Endpoint**: `https://catalogue.dataspace.copernicus.eu/stac`
- **Auth Endpoint**: `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`
- **Documentation**: [Copernicus Data Space Ecosystem APIs](https://dataspace.copernicus.eu/analyse/apis)

### 2.2. Authentication & Authorization

Unlike the Planetary Computer which uses a SAS token signing mechanism (via `planetary-computer` package), CDSE requires:

- **Search**: Public/Open (no auth required).
- **Download**: Requires an OAuth2 Bearer token in the HTTP header.
    - **Flow**: Resource Owner Password Credentials Grant (Username/Password) or Client Credentials.
    - **Token Lifecycle**: Tokens expire (usually 600s). The system must handle generation and refresh (or re-generation on 401).

### 2.3. Dependencies

- **Current**: `pystac-client`, `requests`.
- **Decision**: **Keep it Simple.** Do not add heavy dependencies like `sentinelsat` or `eodag` solely for this. We will implement a lightweight `CopernicusAuth` class (or function) using `requests` to handle token retrieval. This maintains the "Educational Architect" philosophy by showing how OAuth2 flows work under the hood.

### 2.4. Codebase Impact

- **`src/geospatial_tools/utils.py`**:

    - **Modification**: Update `download_url` to accept an optional `headers: dict` argument. This is a non-breaking change that enables passing `Authorization: Bearer <token>`.

- **`src/geospatial_tools/stac.py`**:

    - **Constants**: Add `COPERNICUS` catalog name and API URLs.
    - **Auth Handler**: Create a helper (e.g., `get_copernicus_token` or a simple `CopernicusSession` class) to manage credentials and token fetching.
    - **`StacSearch` Class**:
        - Needs to be aware of the authentication context for downloads.
        - **Refactoring**: Update `_download_assets` to retrieve necessary headers based on the `catalog_name` before calling `download_url`.

## 3. Implementation Plan

### Phase I: Foundation (Utilities & Config)

- [x] **Update `utils.download_url`**: Modify signature to `def download_url(..., headers: dict | None = None)`.
- [x] **Credential Management**:
    - Define standard environment variables: `COPERNICUS_USERNAME`, `COPERNICUS_PASSWORD`.
    - *Educational Note*: Explain why we use env vars (security, 12-factor app) vs hardcoding.

### Phase II: Authentication Logic

- [ ] **Implement `get_copernicus_credentials`**: A helper to safely retrieve env vars or prompt the user (if running interactively/CLI) and warn if missing.
- [ ] **Implement `get_copernicus_token`**: A function that:
    1. Checks for cached valid token (optional optimization for later).
    2. Posts credentials to the Auth Endpoint.
    3. Returns the access token string.
    4. Handles errors (401, connection issues) with clear logging.

### Phase III: STAC Integration

- [x] **Update `catalog_generator`**: Add support for `COPERNICUS` catalog name.
- [ ] **Update `StacSearch`**:
    - In `_download_assets` (and other download methods), add logic to check `self.catalog_name`.
    - If `COPERNICUS`, call `get_copernicus_token` and construct `{"Authorization": f"Bearer {token}"}`.
    - Pass these headers to `download_url`.

### Phase IV: Verification & Documentation

- [ ] **Test Script**: Create `tests/manual_copernicus_test.py` (or similar) to:
    1. Authenticate.
    2. Search for a specific Sentinel-2 tile.
    3. Download a single band (e.g., TCI or B04).
- [ ] **Documentation**: Update `README.md` or `docs/` with instructions on how to set up Copernicus credentials.

## 4. Failure Mode Analysis (FMEA)

| Failure Mode                           | Impact                   | Mitigation                                                                                                                                                |
| :------------------------------------- | :----------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Token Expiry during large download** | Download fails with 401. | **Simple**: Fail and log clearly. **Advanced**: Implement a retry decorator that refreshes token on 401 (Out of scope for initial POC, but good to note). |
| **Missing Credentials**                | Runtime error.           | Check credentials *before* starting the search/download workflow and provide a helpful error message explaining how to set env vars.                      |
| **API Rate Limiting**                  | 429 Errors.              | Ensure `download_url` (or the retry logic in `stac.py`) respects `Retry-After` headers or implements exponential backoff.                                 |

## 5. Educational Opportunities

- **OAuth2 Implementation**: Great opportunity to teach how Bearer tokens work compared to SAS tokens (Planetary Computer).
- **Dependency Injection**: Discuss why we modify `download_url` to take headers rather than hardcoding auth logic inside it.
- **Environment Variables**: Reinforce security best practices.
