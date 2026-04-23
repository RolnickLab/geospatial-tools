---
name: software-dev
description: Unified Software Development, ML, Analytics & Infrastructure Protocol
---
# Software Development Protocol

## Primary Directive
**MANDATE:** Elevate research into robust, maintainable, and type-safe systems. Apply these standards to all Python development, system design, ML/geospatial processing, analytics, and infrastructure tasks.

## 1. Python & QA Standards
- **Strict Typing:** ALL function arguments and return values MUST have type hints. Use `X | Y` format.
- **Paths:** ALWAYS use `pathlib.Path`. Never `os.path`.
- **Logging:** Use `structlog`. NEVER `print()`.
- **Data Structures:** Use `@dataclass` or `Pydantic`. No untyped dictionaries for complex state.
- **Documentation:** Google Style docstrings. Follow Diátaxis framework. No types in docstrings (use hints).
- **Automation:** Orchestrate via `Makefile`.
    - Use `make targets` to discover available targets.
    - Use `make info` for project environment and configuration info.
    - Use `make precommit` and `make test`.
- **Existing project knowledge:** Consult [docs/agents/instructions/KNOWLEDGE.md](KNOWLEDGE.md). Extend when necessary.
- **Finding and fixing bugs:** Use [docs/agents/instructions/root_cause_analysis.md](root_cause_analysis.md) instructions.

## 2. System Design & Architecture
- **Separation of Concerns:** Isolate data acquisition (STAC/S3) from processing logic. Avoid "God Objects".
- **Config-First:** Centralize all parameters in `configs/geospatial_tools_ini.yaml` (parsed via Pydantic).
- **Idempotency:** Design pipelines to be resumeable and safe to run multiple times.

## 3. ML & Geospatial Processing

- **Explicit CRS:** Always handle Coordinate Reference Systems (
  `rasterio.crs.CRS.from_epsg()`). Assert CRS matches before joins/calculations.
- **Memory Management:** Use windowed reading (`rasterio`) or lazy evaluation (`dask`/`xarray`) for rasters > 100MB.
- **Reproducibility:** Set global random seeds. Use geographic region splitting for spatial cross-validation to avoid autocorrelation leakage.
- **Output Formats:** Default to COG, Parquet (Snappy/Zstd), or Zarr.

## 4. Analytics & Visualization
- **EDA Workflow:** Profile for `NaN`/nodata first. Harmonize CRS before spatial analysis.
- **Visual Integrity:** Use perceptually uniform colormaps (`viridis`, `plasma`). No rainbow maps or pie charts. Provide geographic context (basemaps/borders).
- **Notebook Hygiene:** Ensure top-down sequential execution. No hidden state.

## 5. Infrastructure & Environment
- **Dependency Management:** Use `uv` and `uv.lock`. Run tasks in `nox` or `uv` environments.
- **IaC & Containers:** Prefer `Terraform`/`Pulumi`. Use multi-stage Docker builds. Containers MUST NOT run as root.
- **HPC:** Explicitly request SLURM resources (CPUs, memory).

## Consolidated Forbidden Patterns
- ❌ **Secrets:** No hardcoded tokens/keys in code, scripts, or Dockerfiles.
- ❌ **QA Bypass:** No committing code that fails `pre-commit`. No manual dependency additions.
- ❌ **Silent Failures:** No bare `except: pass`. No silent OOMs or nodata averaging.
- ❌ **Global/Magic State:** No global mutable variables. No magic numbers/strings (use configs).
- ❌ **Inefficient Ops:** No Python loops for array processing (use vectorization). No loading massive rasters into RAM.
- ❌ **Analytical Bias:** No fitting on test data. No "magic" outlier removal. No misleading visualizations.
