# Machine Learning & Geospatial Processing Instructions

\<primary_directive>
Your goal is to help build state-of-the-art models and data pipelines that are reproducible, reliable, and well-documented.
**MANDATE:** Apply the project-specific rules outlined below for all ML and geospatial processing tasks.
\</primary_directive>

<context>
This project deals heavily with geospatial datasets (Sentinel-2, Radar, etc.) which introduce unique memory and projection challenges compared to standard ML pipelines.
</context>

<standards>
You MUST enforce the following project-specific standards:

### 1. Geospatial Data Handling

- **Explicit CRS:** Always explicitly handle Coordinate Reference Systems (`rasterio.crs.CRS.from_epsg()`). Do not assume unprojected data is WGS84 without verification.
- **Memory Management:** For large datasets (e.g., geospatial rasters > 100MB), you MUST use windowed reading (via `rasterio` windows) or lazy evaluation (via `dask` and `xarray`) to prevent Out-Of-Memory (OOM) errors.
- **Modern Libraries:** Utilize `xarray`, `rioxarray`, and `geopandas` for multidimensional and vector operations.
- **Output Formats:** Default to writing outputs as Cloud Optimized GeoTIFFs (COG), Parquet (Snappy/Zstd compressed), or Zarr archives for optimal cloud-native read access.

### 2. Model Training & Evaluation

- **Deterministic Execution:** ALWAYS set random seeds globally to ensure reproducibility across experimental runs.

- **Strict Isolation:** NEVER leak spatial information between train, validation, and test sets. Ensure spatial cross-validation is used (e.g., splitting by geographic regions) rather than random pixel splitting, to avoid spatial autocorrelation leakage.

- **Config-Driven:** Hyperparameters and dataset paths MUST be externalized to configuration files and loaded via Pydantic models.

    </standards>

\<forbidden_patterns>

- ❌ **Silent OOMs:** You MUST NOT write data loaders that attempt to load massive raster datasets entirely into RAM.
- ❌ **Ignoring CRS:** You MUST NEVER perform spatial joins or distance calculations without first asserting both datasets share the exact same CRS.
- ❌ **Fitting on Test Data:** You MUST NEVER allow data transformations to be fitted on the validation or test sets.
    \</forbidden_patterns>
