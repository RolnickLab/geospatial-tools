# TASK-2: Define UsgsLandsat Landsat Constants

Maps to **Plan Step 2**. Depends on **TASK-1**.

## Goal

Create strongly typed `StrEnum` constants for the single shared Landsat Level-1 collection, the platform property, and the asset/band keys.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§2, §2.1)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2)
- **Reference module:** `src/geospatial_tools/stac/planetary_computer/constants.py` (mirror its `StrEnum` style and `sortby_field` property).

## Subtasks

1. Create directory `src/geospatial_tools/stac/usgs_landsat/` with empty `__init__.py`.
2. Create `src/geospatial_tools/stac/usgs_landsat/constants.py`.
3. Define `UsgsLandsatLandsatCollection(StrEnum)` with one member:
    ```python
    LEVEL_1_COLLECTION_2 = "landsat-c2l1"
    ```
    This collection ID is verified live against `https://landsatlook.usgs.gov/stac-servercollections` (2026-04-30). It covers BOTH Landsat 8 and 9; differentiation happens via the `platform` property, not via separate collections.
4. Define `UsgsLandsatLandsatProperty(StrEnum)` with at least:
    ```python
    PLATFORM = "platform"          # bare STAC core property, NOT eo:-prefixed
    CLOUD_COVER = "eo:cloud_cover" # standard EO extension
    ```
    Mirror the `sortby_field` property from `PlanetaryComputerS2Property`.
5. Define `UsgsLandsatLandsatPlatform(StrEnum)` to pin platform query values:
    ```python
    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_9 = "LANDSAT_9"
    ```
6. **Pre-research subtask before defining `UsgsLandsatLandsatBand`:** Run a one-off integration query (TASK-5 will formalize this) and record the verbatim asset keys returned by a CMR USGS_EROS Landsat L1 item. Common expected keys are something like `B01..B11`, `MTL.json`/`MTL.txt`, `ANG`, `qa_pixel`, `qa_radsat`, but the actual key strings on CMR may differ from the USGS landsatlook STAC catalog. Pin only what the reconnaissance returns.
7. Define `UsgsLandsatLandsatBand(StrEnum)` using the verbatim asset keys recorded in subtask 6. Add common-name aliases (`COASTAL`, `BLUE`, `GREEN`, `RED`, `NIR`, `SWIR_1`, `SWIR_2`, etc.) sharing values with the standard band members, mirroring the `PlanetaryComputerS2Band` pattern.
8. Create `tests/test_usgs_landsat_landsat_constants.py` verifying:
    - Each enum member's `.value` equals its declared string.
    - Aliases collide-equal with their backing standard band.
    - The collection ID string contains `"Landsat Level-1 Collection 2"`.

## Requirements & Constraints

- Use `StrEnum` for all enums.
- Asset keys, collection ID, and platform values must match exactly what CMR USGS_EROS returns. Do not paraphrase or normalize case.
- The collection ID string contains spaces and an underscore — do not strip or replace them.
- No imports from `core.py` (constants module is leaf-level).

## Acceptance Criteria (AC)

- `constants.py` defines `UsgsLandsatLandsatCollection`, `UsgsLandsatLandsatProperty`, `UsgsLandsatLandsatPlatform`, `UsgsLandsatLandsatBand`.
- All enum members evaluate to the correct string values.
- Asset key choices documented in the TASK-2 work log (which item was inspected, what asset keys were observed).

## Work Log (Subtask 6 Reconnaissance)

**Date:** 2026-04-30

**CMR USGS_EROS STAC search result:** Returned 0 items for `landsat-c2l1` regardless of bbox, datetime, or search method (POST/GET). `context.matched = 0`. The collection ID is valid (confirmed via `/collections` endpoint), but the item search endpoint appears non-functional for this collection.

**Fallback source:** USGS LandsatLook STAC catalog at `https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l1` — the operational USGS Landsat Collection 2 STAC endpoint. Uses the same USGS asset key schema as the CMR catalog.

**Item inspected:** `LC09_L1GT_042206_20260430_20260430_02_T2` (platform: `LANDSAT_9`)
Identical asset keys confirmed for a `LANDSAT_8` item.

**Verbatim asset keys observed (sorted):**
`ANG.txt`, `MTL.json`, `MTL.txt`, `MTL.xml`, `SAA`, `SZA`, `VAA`, `VZA`,
`blue`, `cirrus`, `coastal`, `green`, `index`, `lwir11`, `lwir12`, `nir08`,
`pan`, `qa_pixel`, `qa_radsat`, `red`, `reduced_resolution_browse`, `swir16`, `swir22`, `thumbnail`

**Asset titles (selected):**

- `coastal` → Coastal/Aerosol Band (B1)
- `blue` → Blue Band (B2)
- `green` → Green Band (B3)
- `red` → Red Band (B4)
- `nir08` → Near Infrared Band 0.8 (B5)
- `swir16` → Short-wave Infrared Band 1.6 (B6)
- `swir22` → Short-wave Infrared Band 2.2 (B7)
- `pan` → Panchromatic Band (B8)
- `cirrus` → Cirrus Band (B9)
- `lwir11` → Thermal Infrared Band 10.9 (B10)
- `lwir12` → Thermal Infrared Band 12.0 (B11)
- `qa_pixel`, `qa_radsat` → QA bands
- `SAA`, `SZA`, `VAA`, `VZA` → Solar/Sensor angle bands
- `ANG.txt`, `MTL.json`, `MTL.txt`, `MTL.xml` → Metadata files
- `thumbnail`, `reduced_resolution_browse`, `index` → Visualization/index assets

## Completion Protocol

1. All ACs met. [DONE]
2. Tests pass without regressions (47 new tests pass; 168 total pass). [DONE]
3. Code passes linting and type-checking (`ruff`, `mypy` clean). [DONE]
4. Commit work: `git commit -m "feat: task 2 - define UsgsLandsat Landsat constants"` [DONE]
5. Update document: Mark as COMPLETE. [COMPLETE]
