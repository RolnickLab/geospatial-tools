# Refactor Copernicus Data Access to S3 Protocol

## 1. Scope & Context

**Problem:** Currently, the `geospatial_tools.stac` module downloads Copernicus Sentinel-2 data using HTTP(S) links provided in the STAC item assets (`href`). These links often redirect to S3 buckets, but direct access via `boto3` is more efficient, robust, and standard for cloud-native geospatial workflows. The user specifically requested switching to `boto3` for downloading data from the S3 buckets pointed to by these hrefs.

**Context:** The project uses `pystac` and `pystac-client` for searching. The download logic is currently mixed within `stac.py` and relies on `requests` (via `geospatial_tools.utils.download_url`) with a token obtained from `geospatial_tools.auth`. We need to introduce `boto3` for S3 interaction while maintaining the existing STAC search capabilities.

**Constraints:**

- Must adhere to project structure and guidelines (use `pathlib`, `structlog`, etc.).
- Must ensure authentication for S3 access is handled correctly (likely using the same credentials or keys provided by the Copernicus Data Space Ecosystem).
- The refactor should be modular and not break existing Planetary Computer functionality.

## 2. Architectural Approach (Trade-offs & Strategy)

**Strategy:**
We will decouple the "download" logic from the `StacSearch` class. Instead of a monolithic `_download_assets` method that assumes HTTP, we will implement a strategy pattern or a simple dispatcher based on the catalog type or asset URL protocol (s3:// vs https://).

Since Copernicus Data Space Ecosystem (CDSE) provides S3-compatible access, we need to configure a `boto3` client with the correct endpoint URL and credentials.

**Key Components:**

1. **S3 Client Factory:** A dedicated function/class to instantiate a `boto3` client (or `botocore` session) specifically configured for Copernicus CDSE endpoint.
2. **Download Strategy:** A `Downloader` protocol/abstraction.
    - `HttpDownloader`: Existing logic using `requests`.
    - `S3Downloader`: New logic using `boto3`.
3. **URL Parsing:** Logic to extract bucket and key from the STAC asset `href`. Note: CDSE STAC hrefs might still be HTTPS URLs that need to be converted to S3 paths or simply treated as S3 keys if we know the bucket structure. *Assumption: The user mentioned the href points to an S3 bucket, so we will treat it as needing S3 access.*
4. **Credential Management:** The existing `get_copernicus_credentials` retrieves username/password. For S3 access, CDSE typically requires generating EC2 credentials or using Access/Secret keys. We will use the standard `boto3` auth mechanism. Since the project now uses `python-dotenv`, we will store these credentials in the `.env` file and update `.env.example`.

**Example `.env` configuration:**

```env
COPERNICUS_USERNAME="your_username"
COPERNICUS_PASSWORD="your_password"
# S3 Credentials for CDSE (Copernicus Data Space Ecosystem)
AWS_ACCESS_KEY_ID="your_access_key"
AWS_SECRET_ACCESS_KEY="your_secret_key"
COPERNICUS_S3_ENDPOINT="https://eodata.dataspace.copernicus.eu"
```

*Assumption: Standard AWS environment variables (or those loaded via dotenv) will be picked up by boto3, but we might need to explicitly pass the `endpoint_url`.*

**Trade-offs:**

- *Complexity vs. Performance:* Adding `boto3` adds a dependency and configuration complexity but offers better performance and reliability for large datasets compared to HTTP streams.
- *Abstraction:* strictly separating downloaders might seem like overkill if we only have two sources, but it aligns with the "Separation of Concerns" directive in `systemdesign.md`.

## 3. Verification & Failure Modes (FMEA)

**Risks:**

- **Credential Mismatch:** S3 access might require different credentials than the REST API token. We need to ensure the user knows how to supply these.
- **Dependency Hell:** `boto3` is heavy.
- **URL format:** The STAC `href` might not be a direct `s3://` URI. We might need to transform `https://zipper.dataspace.copernicus.eu/...` to the correct S3 key.

**Test Strategy:**

- **Unit Tests:** Mock `boto3` client to verify that `download_file` is called with correct bucket and key.
- **Integration Test:** Run `test_copernicus.py` (marked `@pytest.mark.online`) to verify real download. This will require valid S3 credentials in the environment.

## 4. Granular Implementation Steps

1. **Dependency Management:**

    - Add `boto3` to `pyproject.toml` (if not present).

2. **Credential & Auth Update (`geospatial_tools/auth.py`):**

    - Investigate/Implement retrieval of S3-specific credentials if they differ from standard login.
    - **Update `.env.example` and the project's local `.env` with S3 credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `COPERNICUS_S3_ENDPOINT`).**
    - Ensure `python-dotenv` is properly initialized (likely in `auth.py` or `__init__.py`) to load these variables.

3. **S3 Helper Module (`geospatial_tools/s3_utils.py` - New):**

    - Create a module to wrap `boto3`.
    - Function `get_s3_client(endpoint_url: str, ...)`
    - Function `parse_s3_url(url: str) -> tuple[str, str]` (Bucket, Key).

4. **Refactor `stac.py`:**

    - Extract download logic from `_download_assets`.
    - Create `download_asset(asset_url: str, destination: Path, method: str = "http")`.
    - Implement the logic: If `method="s3"` (or inferred from URL/Catalog), use `s3_utils`.
    - Update `_download_assets` in `StacSearch` to delegate to this new function.
    - Specifically for Copernicus, ensure we use the S3 method.

5. **Update `test_copernicus.py`:**

    - Add a test case for S3 download.

## 5. Next Step

Do you approve this plan to refactor `stac.py` and introduce `boto3` for Copernicus S3 downloads?
