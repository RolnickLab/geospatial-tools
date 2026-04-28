# TASK-4: Implement Landsat8Search & Landsat9Search

## Goal

Implement the concrete wrapper classes for Landsat 8 and Landsat 9 and expose them in the package `__init__.py`.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md
- **Existing Code**: `src/geospatial_tools/stac/usgs/landsat.py`, `src/geospatial_tools/stac/usgs/__init__.py`

## Subtasks

1. [ ] Implement `Landsat8Search(AbstractLandsat)` in `landsat.py`. Hardcode the platform query to `"LANDSAT_8"`.
2. [ ] Implement `Landsat9Search(AbstractLandsat)` in `landsat.py`. Hardcode the platform query to `"LANDSAT_9"`.
3. [ ] Ensure `_build_collection_query` returns `{"platform": {"eq": "LANDSAT_X"}}` merged with any other custom queries.
4. [ ] Export `Landsat8Search`, `Landsat9Search`, and the constants classes in `src/geospatial_tools/stac/usgs/__init__.py`.
5. [ ] Add mock-based unit tests in `tests/test_usgs_landsat.py` verifying that `search()` correctly constructs the payload sent to `StacSearch.search` (verifying `platform` is injected).

## Requirements & Constraints

- Must use the `UsgsLandsatCollection.C2L1` collection by default.
- Must inject the exact strings `"LANDSAT_8"` and `"LANDSAT_9"` required by the USGS STAC API.

## Acceptance Criteria (AC)

- [ ] `Landsat8Search()._build_collection_query()` includes `{"platform": {"eq": "LANDSAT_8"}}`.
- [ ] `Landsat9Search()._build_collection_query()` includes `{"platform": {"eq": "LANDSAT_9"}}`.
- [ ] Classes are importable via `from geospatial_tools.stac.usgs import Landsat8Search`.

## Testing & Validation

- **Command**: `make test`
- **Success State**: Unit tests validating the query payload injection pass.
- **Manual Verification**: Run `make precommit`, `make pylint`, `make mypy`.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: task 4 - implement Landsat 8 and 9 search wrappers"`
6. [ ] Update this document: Mark as COMPLETE.
