# TASK-3: Implement AbstractLandsat Base Class

## Goal

Implement the shared `AbstractLandsat` base class that encapsulates common logic for querying the USGS Landsat catalog.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md
- **Existing Code**: `src/geospatial_tools/stac/usgs/landsat.py` (new)

## Subtasks

1. [ ] Create `src/geospatial_tools/stac/usgs/landsat.py`.
2. [ ] Implement `AbstractLandsat(AbstractStacWrapper)` base class.
3. [ ] Override `__init__` to swap the underlying client to `StacSearch(USGS)` — `AbstractStacWrapper.__init__` hardcodes `StacSearch(PLANETARY_COMPUTER)` at `core.py:904`, so the override is the only seam available without refactoring the base. After calling `super().__init__(...)`, replace `self.client` with a `StacSearch(USGS)` instance configured with the same retry parameters.
4. [ ] Implement `_build_collection_query(self)` method in `AbstractLandsat`. Since both Landsat 8 and 9 will filter by platform, leave a hook (e.g. abstract property `platform` or an abstract method) for concrete classes to supply their specific platform string, and include it in the query.
5. [ ] Default the `collections` argument used by the wrapper to `[UsgsLandsatCollection.C2L1]`.
6. [ ] Create `tests/test_usgs_landsat.py` with mock-based unit tests to verify `AbstractLandsat` instantiates correctly with the USGS catalog and fails if instantiated directly without abstract method implementations.

## Requirements & Constraints

- Must inherit from `AbstractStacWrapper` in `stac/core.py`.
- Must set the STAC client to target the USGS catalog (`self.client.catalog_name == USGS`).
- Must remain abstract (not directly instantiable).
- Must not require an auth module or a download-path branch — verified anonymous (see plan §2.1).

## Acceptance Criteria (AC)

- [ ] `AbstractLandsat` targets the USGS catalog (`self.client.catalog_name == USGS`).
- [ ] Attempting to instantiate `AbstractLandsat` directly raises a `TypeError`.

## Testing & Validation

- **Command**: `make test`
- **Success State**: Unit tests verifying the abstract nature and correct catalog target pass.
- **Manual Verification**: Run `make precommit`, `make pylint`, `make mypy`.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: task 3 - implement AbstractLandsat base class"`
6. [ ] Update this document: Mark as COMPLETE.
