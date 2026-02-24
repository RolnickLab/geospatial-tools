# Copernicus STAC Catalog Integration Plan

## 1. Objective

Integrate the Copernicus Data Space Ecosystem (CDSE) STAC catalog into the `geospatial_tools` library, enabling users to search and download Sentinel data (and other Copernicus products) alongside the existing Planetary Computer integration.

## 2. Analysis & Requirements

### 2.1. Target API

- **Endpoint**: The Copernicus Data Space Ecosystem STAC API endpoint is likely `https://catalogue.dataspace.copernicus.eu/stac`.
- **Documentation**: [Copernicus Data Space Ecosystem APIs](https://dataspace.copernicus.eu/analyse/apis)

### 2.2. Authentication & Authorization

Unlike the Planetary Computer which uses a SAS token signing mechanism (via `planetary-computer` package), CDSE typically requires:

- **Search**: Generally open/public for metadata.
- **Download**: Requires authentication (OAuth2 / Keycloak).
    - Users need to register at [dataspace.copernicus.eu](https://dataspace.copernicus.eu/).
    - Access tokens are obtained via credentials (username/password or client credentials).
    - The token must be passed in the `Authorization` header (Bearer token) when downloading assets.

### 2.3. Dependencies

- **Current**: `pystac-client`, `requests`.
- **New Needs**:
    - Mechanism to handle OAuth2 token generation.
    - We might need to add a dependency or implement a simple auth handler using `requests`.
    - `sentinelsat` is a common tool but we are focusing on STAC.
    - `eodag` is another option, but we are building a lightweight wrapper.
    - **Decision**: Implement a lightweight auth handler in `utils.py` or `stac.py` to keep dependencies low, or check if a CDSE python client exists that fits our needs.

### 2.4. Codebase Impact

- **`src/geospatial_tools/stac.py`**:

    - Add `COPERNICUS` constant.
    - Add `COPERNICUS_API` URL.
    - Implement `create_copernicus_catalog` function.
    - Update `catalog_generator` to include Copernicus.
    - **Challenge**: The current `Asset` and `StacSearch` classes rely on `download_url` in `utils.py`.
    - **Refactoring**: `download_url` might need to accept headers or an `Auth` object. Alternatively, `StacSearch` might need a strategy pattern for downloading assets depending on the catalog source.

- **`src/geospatial_tools/utils.py`**:

    - `download_url` currently takes a simple URL. It may need to be enhanced to support authenticated sessions or headers.

## 3. Implementation Plan

### Phase I: Blueprint & Design

Go through each step below and update this document with your results. Do not implement yet.

- [ ] Confirm the exact STAC API endpoint.
- [ ] Design the authentication flow and update subsequent phases with your findings.
    - User provides username/password in env vars (e.g., `COPERNICUS_USERNAME`, `COPERNICUS_PASSWORD`).
    - Also consider that user should be able in input username and password through the command line
    - User should be able to use .env file for this too, to simplify repeat use.
    - Add a mechanism to warn the user is not authentication is found, and create the .env file for the user with the provided input
- [ ] Define how `StacSearch` will handle the download difference between Planetary Computer (signed URLs) and Copernicus (Bearer token).

### Phase II: Foundation (Infrastructure)

- [ ] Add necessary environment variable handling for credentials.
- [ ] Update `pyproject.toml` if a new auth library is strictly necessary (try to avoid).

### Phase III: Implementation

1. **`stac.py`**:
    - Define `COPERNICUS_STAC_API_URL`.
    - Implement `create_copernicus_catalog`.
2. **Authentication**:
    - Implement a helper to fetch the access token from CDSE auth endpoint (`https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`).
3. **Download Logic**:
    - Modify `StacSearch._download_assets` to check which catalog is being used or check if the asset href requires auth.
    - Update `download_url` in `utils.py` to support headers.

### Phase IV: Integration & Verification

- [ ] Create a test script to search for a Sentinel-2 scene on Copernicus STAC.
- [ ] Verify download works with valid credentials.
- [ ] Ensure Planetary Computer functionality remains unbroken.

## 4. Failure Mode Analysis (FMEA)

- **Token Expiry**: Access tokens expire. The download process must handle 401 errors and refresh the token.
- **Rate Limiting**: CDSE has rate limits. Implement backoff strategies (already partially in `download_url`? No, `download_url` is simple. `stac.py` has retries for search, but not explicitly for download).
- **Missing Credentials**: Clear error messages if user tries to download without credentials.

## 5. Questions for User

- Do you have a preference for how to handle credentials (env vars vs config file)?
- Are you targeting specifically the Copernicus Data Space Ecosystem (CDSE)?
