# TASK-2: Define USGS Landsat Constants

## Goal

Create strongly typed Enum constants representing USGS Landsat collections, properties, and bands.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md
- **Existing Code**: `src/geospatial_tools/stac/usgs/constants.py` (new)

## Subtasks

1. [ ] Create directory `src/geospatial_tools/stac/usgs/` with an empty `__init__.py`.
2. [ ] Create `src/geospatial_tools/stac/usgs/constants.py`.
3. [ ] Define `UsgsLandsatCollection` Enum (e.g. `C2L1 = "landsat-c2l1"`).
4. [ ] Define `UsgsLandsatProperty` Enum (e.g. `PLATFORM = "platform"`, `CLOUD_COVER = "eo:cloud_cover"`).
5. [ ] Define `UsgsLandsatBand` Enum mapping to expected USGS STAC asset keys for Level-1 TOA (e.g. `COASTAL = "coastal"`, `BLUE = "blue"`, `GREEN = "green"`, `RED = "red"`, `NIR08 = "nir08"`, `SWIR16 = "swir16"`, `SWIR22 = "swir22"`, `PAN = "pan"`, `CIRRUS = "cirrus"`, `LWIR11 = "lwir11"`, `LWIR12 = "lwir12"`, `QA_PIXEL = "qa_pixel"`).
6. [ ] Create `tests/test_usgs_landsat_constants.py` to verify Enum values.

## Requirements & Constraints

- Use `StrEnum` for all classes to maintain consistency with `planetary_computer/constants.py`.
- Asset keys must match the exact strings returned by `https://landsatlook.usgs.gov/stac-server` for the `landsat-c2l1` collection.

## Acceptance Criteria (AC)

- [ ] Constants file defines collections, properties, and bands.
- [ ] Enum members correctly evaluate to their string equivalents.

## Testing & Validation

- **Command**: `make test`
- **Success State**: Constants tests pass.
- **Manual Verification**: Run `make precommit`, `make pylint`, `make mypy` to ensure style and types are correct.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: task 2 - define USGS Landsat constants"`
6. [ ] Update this document: Mark as COMPLETE.
