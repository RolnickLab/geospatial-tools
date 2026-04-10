# SPEC: Persistence Layer for STAC Assets

## 1. Overview

- **Goal**: Create a local persistence layer for downloaded and processed STAC satellite imagery products using STAC GeoParquet and DuckDB to facilitate building spatio-temporal multi-datasource time series data cubes and to enable the seamless reconstitution of native `Asset` objects for subsequent analysis sessions.
- **Problem Statement**: We need to construct spatio-temporal data cubes from STAC items. However, traditional RDBMS solutions (like pgSTAC) are prohibited in our HPC and local workstation environments due to a strict "no-daemon" constraint. We need a highly concurrent, in-process, file-backed local catalog that strictly adheres to geospatial metadata best practices (CRS alignment, COG formats), allows us to persist and later reload downloaded products as native python objects, and supports multi-datasource heterogeneity.

## 2. Requirements & Traceability Mapping

### Functional Requirements

- [ ] **Requirement 1** (Mapped to `src/geospatial_tools/stac.py::Asset`): Enforce that if an `Asset` has been merged (`merged_asset_path` is not None), the underlying `pystac.Item` must be dynamically updated. The unmerged individual sub-item assets must be removed from the STAC item's assets dictionary, and a new single `pystac.Asset` pointing to the merged raster must be added.
- [ ] **Requirement 2** (Mapped to `src/geospatial_tools/stac.py::Asset`): **Metadata Preservation & Creation**: The newly created `pystac.Asset` for a merged product must aggregate `eo:bands` metadata from its original sub-items. It must also explicitly extract and store `proj:epsg`, `proj:transform`, and `proj:shape` from the physical merged raster (which must be a Cloud Optimized GeoTIFF) to guarantee CRS alignment ("CRS is Law").
- [ ] **Requirement 3** (Mapped to `src/geospatial_tools/persistence/models.py`): **Multi-Datasource Schema Evolution**: Implement Pydantic serialization models that map `Asset` attributes and their underlying updated `pystac.Item` references to the stac-geoparquet specification. The `properties` mapping must be flexible enough to handle heterogeneous STAC extensions (e.g., EO vs. SAR vs. Datacube) dynamically without schema-locking the Parquet Writer (e.g. by using a unified JSON string representation or robust `union_by_name` ingestion).
- [ ] **Requirement 4** (Mapped to `src/geospatial_tools/persistence/writer.py`): Implement a Parquet Writer that writes serialized objects to discrete, isolated `.parquet` files within a designated shared output directory to support parallel writes.
- [ ] **Requirement 5** (Mapped to `src/geospatial_tools/persistence/query.py`): Implement a Query Interface using an ephemeral, in-memory DuckDB connection loaded with the `spatial` extension.
- [ ] **Requirement 6** (Mapped to `src/geospatial_tools/persistence/query.py`): The Query Interface must execute spatio-temporal bounding box queries against the Parquet directory using glob patterns and return the resulting local file paths (GeoTIFF/Zarr asset URLs) and/or STAC Items.
- [ ] **Requirement 7** (Mapped to `src/geospatial_tools/stac.py::Asset.from_pystac_item`): **Asset Hydration**: Implement a factory method or deserialization mechanism to instantiate a fully functional `Asset` object from a STAC item retrieved via the Query Interface, completing the full lifecycle (Search -> Asset -> Download -> Persist -> Query -> Reconstituted Asset).
- [ ] **Requirement 8** (Mapped to `src/geospatial_tools/datacube.py`): Implement a Data Cube Bridge utility that lazily loads the file paths extracted by DuckDB into an `xarray.Dataset`.
- [ ] **Requirement 9** (Mapped to `src/geospatial_tools/planetary_computer/sentinel_2.py::download_sentinel2_product`): Update the download and merge pipeline to automatically invoke the Parquet Writer upon a successful download or merge.
- [ ] **Requirement 10** (Mapped to `src/geospatial_tools/persistence/writer.py` and `query.py`): **Path Portability**: The persistence layer must guarantee that absolute local file paths are not permanently baked into the Parquet files if those paths differ across environments (e.g., writing on an HPC cluster and reading on a local machine). The system must utilize relative paths within the catalog. Upon reading/hydration, the system must dynamically reconstruct the absolute paths using the path constants (e.g., `DATA_DIR`, `PROJECT_ROOT`) defined in `src/geospatial_tools/__init__.py`.

### Non-Functional Requirements

- **Geospatial Integrity**: All merged/reprojected output rasters must be formatted as Cloud Optimized GeoTIFFs (COG). CRS must be explicitly verified and attached to the STAC metadata.
- **Performance/Concurrency**: The write mechanism must support multiple parallel HPC workers writing simultaneously without any file-locking contention (append-by-file pattern).
- **Robustness (Schema Drift)**: The DuckDB queries must handle evolving schemas or missing columns gracefully across older and newer Parquet files, as well as distinct fields introduced by different datasources (Landsat 8, Sentinel-1, ERA5).
- **Portability**: The resulting GeoParquet dataset must be capable of being moved between file systems (e.g. from HPC to S3 or a local machine) without breaking links to the physical `Asset` files.

## 3. Technical Constraints & Assumptions

- **No Background Daemons**: The solution must be completely serverless and file-backed. No external database servers (e.g., PostgreSQL, pgSTAC).
- **Existing Systems**: Must integrate natively with the project's existing `Asset` and `AssetSubItem` classes, extending them with serialization/deserialization capabilities.
- **Libraries**: Must use DuckDB (with the `spatial` extension), PyArrow, stac-geoparquet specifications, Pydantic, and Xarray/stackstac.

## 4. Acceptance Criteria

- [ ] **AC 1** (Tests `src/geospatial_tools/stac.py::Asset`): Merged `Asset` dynamically updates its underlying `pystac.Item`, strictly removing individual component assets and outputting a single asset record representing the merged raster.
- [ ] **AC 2** (Tests `src/geospatial_tools/stac.py::Asset`): The STAC representation of a merged asset correctly contains aggregated `eo:bands` and physically-verified `proj:epsg`, `proj:transform`, and `proj:shape` metadata extracted from the physical file.
- [ ] **AC 3** (Tests `src/geospatial_tools/persistence/models.py`): `Asset` objects serialize correctly to GeoParquet via Pydantic models, accommodating schema variations across different sensors (e.g., Sentinel-1 vs. Sentinel-2) gracefully.
- [ ] **AC 4** (Tests `src/geospatial_tools/persistence/writer.py`): The Parquet Writer can write multiple isolated `.parquet` files to the same directory without locking errors.
- [ ] **AC 5** (Tests `src/geospatial_tools/persistence/query.py`): DuckDB can successfully query the directory of heterogeneous Parquet files using a glob pattern (e.g., `SELECT * FROM read_parquet('stac_output/**/*.parquet', union_by_name=True)`) and execute `ST_Intersects` or temporal filters.
- [ ] **AC 6** (Tests `src/geospatial_tools/stac.py::Asset.from_pystac_item`): Reconstituted `Asset` objects hydrated from the Query Interface possess all required attributes (`merged_asset_path`, `bands`, etc.) and their methods function identically to a newly downloaded object.
- [ ] **AC 7** (Tests `src/geospatial_tools/persistence/query.py`): The DuckDB query accurately returns a list of local asset file paths.
- [ ] **AC 8** (Tests `src/geospatial_tools/datacube.py`): The Data Cube Bridge function correctly instantiates a lazy `xarray.Dataset` from the list of paths returned by DuckDB.
- [ ] **AC 9** (Tests `src/geospatial_tools/planetary_computer/sentinel_2.py`): The Sentinel-2 pipeline seamlessly integrates the Parquet Writer without breaking existing functionality.
- [ ] **AC 10** (Tests `src/geospatial_tools/persistence/query.py`): Querying and reconstituting `Asset` objects continues to function accurately even if the root directory of the Parquet dataset and the physical imagery files is moved to a new absolute file path on the host system, by utilizing the dynamic path constants in `src/geospatial_tools/__init__.py`.
- [ ] **AC 11** (Tests QA Compliance): Execution of `make test`, `make precommit`, and `make check-pylint` all exit with code `0` locally without manual intervention.

## 5. Dependencies

*Note: All new dependencies required for implementation MUST be installed using `uv add <package>`.*

- `duckdb` (Python package).
- `pyarrow` (for writing Parquet files).
- `pydantic` (for strict schema validation and serialization).
- `rasterio` (for extracting spatial metadata from the physical rasters).
- `xarray` and/or `stackstac` (for bridging to data cubes).
- The `spatial` extension for DuckDB (must be loadable at runtime).

## 6. Out of Scope

- Deploying, managing, or interacting with a persistent database server.
- Modifying or processing the actual raster image data (this layer is strictly for metadata/cataloging).
- Implementing STAC API server capabilities; this is purely for local ingestion and querying for data cube construction.

## 7. Verification Plan

- **QA Validations**:
    - Run `make precommit` to guarantee formatting and base linting compliance.
    - Run `make check-pylint` to guarantee strict Python standard compliance.
    - Run `make test` to guarantee no regressions were introduced to existing modules.
- **Unit Tests**:
    - Test dynamic update of a merged `Asset`'s `pystac.Item` to ensure the new `pystac.Asset` aggregates `eo:bands` and contains valid `proj:*` metadata explicitly matched against a mock physical COG.
    - Test serialization of an unmerged `Asset` to ensure all `AssetSubItem` components are correctly mapped to STAC GeoParquet assets.
    - Test serialization of a merged `Asset` to ensure ONLY the `merged_asset_path` is serialized as an asset, and `AssetSubItem` records are ignored.
    - **Heterogeneous Serialization Tests**: Serialize a mocked Sentinel-1 STAC item and a mocked Sentinel-2 STAC item. Verify that DuckDB can load both Parquet files simultaneously using `union_by_name=True`.
    - Test hydration of an `Asset` object from a mock STAC item dictionary, verifying all attributes (`asset_id`, `bands`, `merged_asset_path`) are correctly restored.
- **Integration Tests**:
    - Use a test fixture to generate multiple isolated Parquet files in a temporary directory.
    - Instantiate a temporary DuckDB connection, load the `spatial` extension, and run a spatio-temporal bounding box query to verify the correct paths are returned across the chunked files.
    - **Portability Test**: Move the temporary directory to a new location. Re-run the DuckDB query and verify that the asset paths returned successfully resolve to the physical files at their new absolute locations.
- **End-to-End Tests**:
    - **Lifecycle Test**: Search -> Download -> Merge -> Persist -> Query DuckDB -> Hydrate `Asset`. Verify the hydrated `Asset` matches the state of the originally merged `Asset` and can perform a subsequent action (e.g., `reproject_merged_asset`).
    - Pass the result from the DuckDB Query Interface to the Data Cube Bridge to confirm an `xarray.Dataset` is successfully materialized using lazy windowed reads.
