# TASK-2: Define Earthdata Landsat Constants

Maps to **Plan Step 2**. Depends on **TASK-1**.

## Goal

Create strongly typed `StrEnum` constants for the single shared Landsat Level-1 collection, the platform property, and the asset/band keys.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§2, §2.1)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2)
- **Reference module:** `src/geospatial_tools/stac/planetary_computer/constants.py` (mirror its `StrEnum` style and `sortby_field` property).

## Subtasks

1. Create directory `src/geospatial_tools/stac/earthdata/` with empty `__init__.py`.
2. Create `src/geospatial_tools/stac/earthdata/constants.py`.
3. Define `EarthdataLandsatCollection(StrEnum)` with one member:
    ```python
    LEVEL_1_COLLECTION_2 = "Landsat Level-1 Collection 2_Collection 2"
    ```
    This collection ID is verified live against `https://cmr.earthdata.nasa.gov/stac/USGS_EROS/collections` (2026-04-30). It covers BOTH Landsat 8 and 9; differentiation happens via the `platform` property, not via separate collections.
4. Define `EarthdataLandsatProperty(StrEnum)` with at least:
    ```python
    PLATFORM = "platform"          # bare STAC core property, NOT eo:-prefixed
    CLOUD_COVER = "eo:cloud_cover" # standard EO extension
    ```
    Mirror the `sortby_field` property from `PlanetaryComputerS2Property`.
5. Define `EarthdataLandsatPlatform(StrEnum)` to pin platform query values:
    ```python
    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_9 = "LANDSAT_9"
    ```
6. **Pre-research subtask before defining `EarthdataLandsatBand`:** Run a one-off integration query (TASK-5 will formalize this) and record the verbatim asset keys returned by a CMR USGS_EROS Landsat L1 item. Common expected keys are something like `B01..B11`, `MTL.json`/`MTL.txt`, `ANG`, `qa_pixel`, `qa_radsat`, but the actual key strings on CMR may differ from the USGS landsatlook STAC catalog. Pin only what the reconnaissance returns.
7. Define `EarthdataLandsatBand(StrEnum)` using the verbatim asset keys recorded in subtask 6. Add common-name aliases (`COASTAL`, `BLUE`, `GREEN`, `RED`, `NIR`, `SWIR_1`, `SWIR_2`, etc.) sharing values with the standard band members, mirroring the `PlanetaryComputerS2Band` pattern.
8. Create `tests/test_earthdata_landsat_constants.py` verifying:
    - Each enum member's `.value` equals its declared string.
    - Aliases collide-equal with their backing standard band.
    - The collection ID string contains `"Landsat Level-1 Collection 2"`.

## Requirements & Constraints

- Use `StrEnum` for all enums.
- Asset keys, collection ID, and platform values must match exactly what CMR USGS_EROS returns. Do not paraphrase or normalize case.
- The collection ID string contains spaces and an underscore — do not strip or replace them.
- No imports from `core.py` (constants module is leaf-level).

## Acceptance Criteria (AC)

- `constants.py` defines `EarthdataLandsatCollection`, `EarthdataLandsatProperty`, `EarthdataLandsatPlatform`, `EarthdataLandsatBand`.
- All enum members evaluate to the correct string values.
- Asset key choices documented in the TASK-2 work log (which item was inspected, what asset keys were observed).

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 2 - define Earthdata Landsat constants"`
5. Update document: Mark as COMPLETE.
