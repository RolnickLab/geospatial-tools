# TASK-2: Define Earthdata Landsat Constants

## Goal

Create strongly typed Enum constants representing Earthdata Landsat collections, properties, and bands.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

1. Create directory `src/geospatial_tools/stac/earthdata/` with empty `__init__.py`.
2. Create `src/geospatial_tools/stac/earthdata/constants.py`.
3. Define `EarthdataLandsatCollection` Enum based on CMR collection ID for Landsat 8/9 Level 1.
4. Define `EarthdataLandsatProperty` Enum (e.g. `PLATFORM = "platform"`, `CLOUD_COVER = "eo:cloud_cover"`).
5. Define `EarthdataLandsatBand` Enum mapping to expected Earthdata STAC asset keys for Level-1 TOA.
6. Create `tests/test_earthdata_landsat_constants.py` to verify Enum values.

## Requirements & Constraints

- Use `StrEnum` for all classes.
- Asset keys and collection IDs must match exactly what `https://cmr.earthdata.nasa.gov/stac/` returns.

## Acceptance Criteria (AC)

- Constants file defines collections, properties, and bands.
- Enum members evaluate to string equivalents correctly.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 2 - define Earthdata Landsat constants"`
5. Update document: Mark as COMPLETE.
