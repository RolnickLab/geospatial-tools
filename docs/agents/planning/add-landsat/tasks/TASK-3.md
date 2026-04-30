# TASK-3: Implement AbstractLandsat Base Class

## Goal

Implement shared `AbstractLandsat` base class encapsulating logic for querying Earthdata Landsat catalog.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

1. Create `src/geospatial_tools/stac/earthdata/landsat.py`.
2. Implement `AbstractLandsat(AbstractStacWrapper)` base class.
3. Override `__init__` to replace `self.client` with `StacSearch(EARTHDATA)` instance.
4. Implement `_build_collection_query(self)`. Leave hook for concrete classes to supply platform string.
5. Default `collections` argument to appropriate `EarthdataLandsatCollection`.
6. Create `tests/test_earthdata_landsat.py` to verify `AbstractLandsat` instantiates correctly and fails if abstract methods missing.

## Requirements & Constraints

- Must inherit from `AbstractStacWrapper`.
- Must set STAC client to target Earthdata catalog.
- Must remain abstract.

## Acceptance Criteria (AC)

- `AbstractLandsat` targets Earthdata catalog (`self.client.catalog_name == EARTHDATA`).
- Instantiating `AbstractLandsat` directly raises `TypeError`.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 3 - implement AbstractLandsat base class"`
5. Update document: Mark as COMPLETE.
