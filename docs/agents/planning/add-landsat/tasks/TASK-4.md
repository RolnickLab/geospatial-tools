# TASK-4: Implement `Landsat8Search` & `Landsat9Search`

Maps to **Plan Step 4** (and Plan Step 8 — init export). Depends on **TASK-3**.

## Goal

Implement concrete wrapper classes for Landsat 8 and Landsat 9 and expose them via the `earthdata` package init.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§2, §4 step 4)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2)
- **Reference:** `src/geospatial_tools/stac/planetary_computer/sentinel_2.py:Sentinel2Search` for the fluent-builder shape.

## Subtasks

1. Implement `Landsat8Search(AbstractLandsat)` in `src/geospatial_tools/stac/earthdata/landsat.py`.
    - Class attribute: `_PLATFORM = EarthdataLandsatPlatform.LANDSAT_8`.
    - Optional fluent helpers (mirror Sentinel-2 shape if useful): e.g. `filter_by_cloud_cover(self, max_cloud_cover: int) -> Self` writing `EarthdataLandsatProperty.CLOUD_COVER` into `custom_query_params`.
2. Implement `Landsat9Search(AbstractLandsat)` analogously with `_PLATFORM = EarthdataLandsatPlatform.LANDSAT_9`.
3. Confirm `_build_collection_query` (inherited from `AbstractLandsat`) produces the platform filter merged with `custom_query_params`.
4. Export classes and constants in `src/geospatial_tools/stac/earthdata/__init__.py`:
    ```python
    from .constants import (
        EarthdataLandsatBand,
        EarthdataLandsatCollection,
        EarthdataLandsatPlatform,
        EarthdataLandsatProperty,
    )
    from .landsat import AbstractLandsat, Landsat8Search, Landsat9Search

    __all__ = [
        "AbstractLandsat",
        "EarthdataLandsatBand",
        "EarthdataLandsatCollection",
        "EarthdataLandsatPlatform",
        "EarthdataLandsatProperty",
        "Landsat8Search",
        "Landsat9Search",
    ]
    ```
5. Add unit tests in `tests/test_earthdata_landsat.py` (shared with TASK-3):
    - `Landsat8Search()._build_collection_query() == {"platform": {"eq": "LANDSAT_8"}}` (assuming no custom params).
    - `Landsat9Search()._build_collection_query() == {"platform": {"eq": "LANDSAT_9"}}`.
    - `Landsat8Search(...).client.catalog_name == EARTHDATA`.
    - `from geospatial_tools.stac.earthdata import Landsat8Search, Landsat9Search` resolves.

## Requirements & Constraints

- Must use `EarthdataLandsatCollection.LEVEL_1_COLLECTION_2` (single shared collection) by default.
- Must inject the exact platform strings via `EarthdataLandsatPlatform`.
- Tests in this task MUST NOT hit the network; integration coverage is TASK-5.

## Acceptance Criteria (AC)

- `Landsat8Search()._build_collection_query()` includes `{"platform": {"eq": "LANDSAT_8"}}`.
- `Landsat9Search()._build_collection_query()` includes `{"platform": {"eq": "LANDSAT_9"}}`.
- Classes importable via `from geospatial_tools.stac.earthdata import Landsat8Search, Landsat9Search`.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 4 - implement Landsat 8/9 search wrappers and earthdata package init"`
5. Update document: Mark as COMPLETE.
