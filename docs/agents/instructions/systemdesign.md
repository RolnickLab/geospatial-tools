# System Design & Architecture Skill Instructions

\<primary_directive>
Your objective is to design systems that are maintainable, evolvable, and robust.
**MANDATE:** Apply the project-specific rules outlined below for all system design and architectural tasks.
\</primary_directive>

<context>
Geospatial research codebases quickly become tangled if data fetching (STAC), processing (Rasterio), and analysis (Xarray) are all handled in the same script.
</context>

<standards>
You MUST enforce the following project-specific architectural patterns:

### 1. Configuration-First Design

- ALL hyperparameters, file paths, auth mechanisms, and STAC catalog endpoints MUST be centralized in a configuration object (e.g., `configs/geospatial_tools_ini.yaml` parsed via Pydantic). Never bury them in processing scripts.

### 2. Separation of Concerns

- **Data Acquisition:** Modules fetching from Planetary Computer or Copernicus must be isolated from the logic that processes the bytes.
- **Processing:** Heavy geospatial processing must rely on clean, injected inputs (e.g., passing a local `pathlib.Path` rather than an S3 URL directly to a processing function, if intermediate storage is preferred).

### 3. Error Handling & Idempotency

- Design pipelines to resume gracefully. If a 100-tile download fails at tile 99, the pipeline must be able to restart and only fetch the missing tile.
    </standards>

\<forbidden_patterns>

- ❌ **God Objects:** You MUST NOT design classes that handle STAC querying, raster clipping, and matplotlib plotting simultaneously.
- ❌ **Hardcoded Configurations:** You MUST NEVER bury STAC endpoints, chunk sizes, or file paths inside logic files.
    \</forbidden_patterns>
