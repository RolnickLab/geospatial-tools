# Plan: Add Persistence Layer for STAC Assets

## 🎯 Scope & Context

The goal is to create a local persistence layer for downloaded and processed satellite imagery products (STAC items). This layer will act as a local catalog to facilitate the construction of spatio-temporal, multi-datasource data cubes (time series) and enable the seamless reconstitution of native `Asset` objects for subsequent sessions. Given the deployment environment (HPC and local workstations) and a strict "no-daemon" constraint, traditional RDBMS solutions like pgSTAC are prohibited. The solution must be in-process and file-backed. It must integrate natively with the existing `Asset` and `AssetSubItem` classes, specifically ensuring that when an `Asset` is merged, only the merged product is persisted as the primary asset, discarding the individual sub-items. Furthermore, the architecture must explicitly support multi-datasource heterogeneity (e.g., Sentinel-1, Sentinel-2, Landsat 8, ERA5) without schema locking.

## 🏗️ Architectural Approach

We will adopt a "Serverless Spatial Engine" architecture, separating the storage format from the query execution using STAC GeoParquet and DuckDB.

- **Metadata Storage (STAC GeoParquet)**: Python objects (`Asset` and its underlying `pystac.Item` reference) will be serialized into partitioned Parquet datasets. This prevents inode exhaustion and I/O throttling on parallel file systems.
- **Geospatial & Metadata Preservation**: Crucially, if an `Asset` has been merged, the serialization process treats the merged multi-band raster as the sole asset. To maintain strict STAC compliance, the underlying `pystac.Item` must be explicitly updated *before* serialization: original `AssetSubItem` assets must be removed and replaced with a single new `pystac.Asset` pointing to the merged raster. This new asset must aggregate `eo:bands` metadata and extract exact spatial metadata (`proj:epsg`, `proj:transform`, `proj:shape`) directly from the merged physical COG.
- **Multi-Datasource Schema Evolution (ETC & Open-Closed Principle)**: Different satellite constellations carry wildly different STAC extensions (e.g., `sat:orbit_state` for Sentinel-1 vs `eo:cloud_cover` for Sentinel-2). To ensure the persistence layer is "Easier to Change" and open to new datasources (like ERA5) without modifying the core writer:
    - DuckDB must be instructed to read Parquet files with schema evolution enabled (`union_by_name=True`).
    - The serialization Pydantic models must use dynamic `**kwargs` or a unified `properties` JSONB/Struct column to encapsulate custom STAC extensions, preventing Parquet schema clashes between different product types.
- **Query Engine (DuckDB + Spatial Extension)**: An ephemeral, in-memory DuckDB connection will query the Parquet files via glob patterns (`SELECT * FROM read_parquet('stac_output/**/*.parquet', union_by_name=true)`). It handles complex spatial intersections and zero-copy results.
- **Object Hydration (Reconstitution)**: The results queried from DuckDB (STAC items in tabular format) are deserialized back into native `pystac.Item` instances, which instantiate fully functional `Asset` objects.
- **Data Cube Bridge (Xarray)**: The filtered asset URLs extracted via DuckDB will be fed directly into `xarray.open_mfdataset()` or `stackstac` to materialize the n-dimensional array, utilizing lazy evaluation and windowed reads.
- **Concurrency Strategy**: To support parallel HPC jobs, each worker will write its own discrete `.parquet` file to a shared output directory, entirely bypassing file-locking contention.

## 🧪 Verification & FMEA

**Test Strategy & QA Mandates**:

- **QA Pipeline**: All newly produced code must pass the project's standard QA and validation tools before being considered complete. This means executing and passing `make test`, `make precommit`, and `make check-pylint` successfully.
- Unit tests verifying that `Asset` objects serialize correctly to GeoParquet, explicitly checking that merged assets produce single-asset records.
- **Heterogeneous Serialization Tests**: Unit tests proving that a Sentinel-1 STAC item (SAR extensions) and a Sentinel-2 STAC item (EO extensions) can be serialized by the same Parquet Writer and successfully queried together by DuckDB.
- Unit tests to verify that `pystac.Item` objects correctly aggregate `eo:bands` and extract physical `proj:*` metadata during the merge operation.
- Integration tests using a temporary DuckDB instance to glob multiple generated Parquet files and execute a spatial bounding box query, validating the correct paths are returned.
- End-to-end lifecycle tests: Search -> Download -> Merge -> Persist -> Query DuckDB -> Reconstitute `Asset` -> Validate reconstituted object's methods.

**Failure Modes & Effects Analysis (FMEA)**:

- **Failure Mode: Write Contention.** Multiple parallel HPC workers attempting to update a single `.db` file or append to a single `.parquet` file simultaneously.
    - **Mitigation:** Enforce an "append-by-file" pattern. Workers write isolated Parquet files. DuckDB acts as a read-only aggregator.
- **Failure Mode: Multi-Datasource Schema Clashes.** Writing a Landsat 8 Parquet file and a Sentinel-1 Parquet file to the same directory causes DuckDB to fail reading due to incompatible columns in the `properties` struct.
    - **Mitigation:** The Parquet Writer must serialize STAC `properties` into a unified schema (e.g., extracting common fields to top-level columns and dumping the rest into a generic JSON string/struct), OR explicitly enforce `union_by_name=True` during DuckDB reads.
- **Failure Mode: Spatial Metadata Drift.** When merging or reprojecting rasters, the resulting physical file's spatial metadata falls out of sync with the logical `pystac.Item` representation.
    - **Mitigation:** The serialization process must explicitly read the physical merged COG file's profile and inject the exact `proj:epsg`, `proj:transform`, and `proj:shape` into the `pystac.Item` prior to Parquet serialization.
- **Failure Mode: Loss of Object State on Reconstitution.** The reconstituted `Asset` object lacks necessary attributes because they were not properly mapped from the persisted `pystac.Item`.
    - **Mitigation:** Ensure the `Asset.from_stac_item()` hydration factory method correctly parses the custom properties and asset HREFs from the `pystac.Item` back into the `Asset` class attributes.
- **Failure Mode: Path Portability/Mobility.** If the absolute file paths are written into the Parquet files, moving the dataset to another environment (or from HPC to a local machine) will break the Data Cube Bridge.
    - **Mitigation:** The Parquet Writer should save relative paths (relative to the persistence root directory), or the Query Interface/Hydration layer must dynamically reconstruct absolute paths based on an environment variable or configuration setting upon read.

## 📝 Implementation Steps & Code Mapping

*Note: Any new libraries required during these steps MUST be added to the project using the `uv add <package>` command.*

1. **Enhance `Asset` Merging Logic** *(Maps to Spec: Req 1, Req 2, AC 1, AC 2)*:
    - Update `src/geospatial_tools/stac.py::Asset` (specifically `merge_asset` and `reproject_merged_asset`) to dynamically update its underlying `pystac.Item` upon merging, replacing sub-items with a single `pystac.Asset` representing the merged COG with aggregated `eo:bands` and physical `proj:*` metadata.
2. **Define Multi-Datasource GeoParquet Serialization Models** *(Maps to Spec: Req 3, AC 3)*:
    - Create a new module (e.g., `src/geospatial_tools/persistence/models.py`) to implement Pydantic models mapping `Asset` attributes to the stac-geoparquet spec. Specifically, design the `properties` mapping to be flexible enough to handle varied STAC extensions (SAR, EO, Datacube) without schema locking.
3. **Implement Parquet Writer** *(Maps to Spec: Req 4, AC 4)*:
    - Create a new module (e.g., `src/geospatial_tools/persistence/writer.py`) capable of writing these serialized objects to isolated `.parquet` files within a defined output directory structure (defaulting to `DATA_DIR` defined in `src/geospatial_tools/__init__.py`), supporting the append-by-file concurrency model. Must address path portability by strictly serializing paths relative to `DATA_DIR`.
4. **Develop DuckDB Query Interface** *(Maps to Spec: Req 5, Req 6, AC 5, AC 7)*:
    - Create a new module (e.g., `src/geospatial_tools/persistence/query.py`) instantiating an in-memory DuckDB connection with the `spatial` extension loaded. Add methods for executing spatio-temporal queries using `read_parquet(..., union_by_name=True)`.
5. **Implement Asset Hydration (Reconstitution)** *(Maps to Spec: Req 7, AC 6)*:
    - Update `src/geospatial_tools/stac.py::Asset` to include a class factory method (`@classmethod def from_pystac_item(cls, item: pystac.Item) -> "Asset"`) that takes a STAC item retrieved from the DuckDB query layer and instantiates a fully functional `Asset` object. Must handle dynamic absolute path reconstruction.
6. **Create Data Cube Bridge** *(Maps to Spec: Req 8, AC 8)*:
    - Create a new module (e.g., `src/geospatial_tools/datacube.py`) that takes the DuckDB query results and lazily loads them into an `xarray.Dataset`.
7. **Update Download Pipeline Integration** *(Maps to Spec: Req 9, AC 9)*:
    - Modify `src/geospatial_tools/planetary_computer/sentinel_2.py::download_sentinel2_product` to invoke the Parquet Writer after a successful download or merge.

## ⏭️ Next Step

Should we proceed with Step 1: Enhance `Asset` Merging Logic to dynamically update the underlying `pystac.Item`?
