# TASK-4: Implement Landsat8Search & Landsat9Search

## Goal

Implement concrete wrapper classes for Landsat 8 and 9 and expose them.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

1. Implement `Landsat8Search(AbstractLandsat)` in `landsat.py`. Hardcode platform query to `"LANDSAT_8"`.
2. Implement `Landsat9Search(AbstractLandsat)` in `landsat.py`. Hardcode platform query to `"LANDSAT_9"`.
3. Ensure `_build_collection_query` returns platform filter merged with custom queries.
4. Export classes and constants in `src/geospatial_tools/stac/earthdata/__init__.py`.
5. Add unit tests in `tests/test_earthdata_landsat.py` verifying query construction.

## Requirements & Constraints

- Must use `EarthdataLandsatCollection` defined in TASK-2.
- Must inject exact platform strings.

## Acceptance Criteria (AC)

- `Landsat8Search()._build_collection_query()` includes `{"platform": {"eq": "LANDSAT_8"}}`.
- `Landsat9Search()._build_collection_query()` includes correct platform filter.
- Classes importable via `from geospatial_tools.stac.earthdata import Landsat8Search`.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 4 - implement Landsat search wrappers"`
5. Update document: Mark as COMPLETE.
