# TASK-3: Refactor `AbstractStacWrapper`; Implement `AbstractLandsat`

Maps to **Plan Step 3**. Depends on **TASK-1**, **TASK-2**.

## Goal

(1) Refactor `AbstractStacWrapper.__init__` to accept a `catalog_name` parameter (instead of hardcoding `PLANETARY_COMPUTER`), so subclasses do not have to create-then-discard a Planetary Computer client. (2) Implement the `AbstractLandsat` base class that targets the new `EARTHDATA` catalog.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§2, §4 step 3)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2)
- **Code to refactor:**
    - `src/geospatial_tools/stac/core.py:904` — `AbstractStacWrapper.__init__` hardcodes `StacSearch(PLANETARY_COMPUTER)`.
    - `src/geospatial_tools/stac/core.py:432-433` — `StacSearch.__init__` initializes an S3 client only when `catalog_name == COPERNICUS`. Confirm new `EARTHDATA` catalog does NOT trigger this branch (no change required if the conditional already guards correctly; verify and add a regression test).
- **Existing callers of `AbstractStacWrapper`:** `Sentinel1Search`, `Sentinel2Search`, `Sentinel3Search` under `src/geospatial_tools/stac/planetary_computer/`. All currently rely on the hardcoded default — keep them functional via a default value.

## Subtasks

1. Refactor `AbstractStacWrapper.__init__` (`core.py:886-910`):
    - Add new parameter: `catalog_name: str = PLANETARY_COMPUTER`.
    - Replace `self.client: StacSearch = StacSearch(PLANETARY_COMPUTER)` with `self.client: StacSearch = StacSearch(catalog_name)`.
    - Default value preserves backward compatibility for `Sentinel1Search`/`Sentinel2Search`/`Sentinel3Search`.
2. Verify `StacSearch.__init__` (`core.py:432-433`) only initializes the S3 client for `COPERNICUS`. Add a unit test `StacSearch(EARTHDATA).s3_client is None` to prevent future regressions.
3. Create `src/geospatial_tools/stac/earthdata/landsat.py`.
4. Implement `AbstractLandsat(AbstractStacWrapper)`:
    - Override `__init__` to call `super().__init__(catalog_name=EARTHDATA, ...)` and to default `collection` to `EarthdataLandsatCollection.LEVEL_1_COLLECTION_2`.
    - Provide an abstract method or class attribute `_PLATFORM: ClassVar[EarthdataLandsatPlatform]` that concrete classes (TASK-4) supply.
    - Implement `_build_collection_query(self) -> dict[str, Any]` that returns `{EarthdataLandsatProperty.PLATFORM.value: {"eq": self._PLATFORM.value}}` plus any `custom_query_params`.
5. Create `tests/test_earthdata_landsat.py` (shared with TASK-4) verifying:
    - `AbstractLandsat` cannot be instantiated directly (raises `TypeError`, since `_PLATFORM` is unset / `_build_collection_query` is abstract).
    - When subclassed for the test, `self.client.catalog_name == EARTHDATA`.
    - Existing Sentinel wrappers still produce `self.client.catalog_name == PLANETARY_COMPUTER` after the parent refactor (regression test in `tests/test_planetary_computer_*` is sufficient if it already runs; otherwise add a small assertion test).

## Requirements & Constraints

- Refactor must NOT change the call sites of `Sentinel1Search`, `Sentinel2Search`, `Sentinel3Search`.
- `AbstractLandsat` remains abstract — direct instantiation raises `TypeError`.
- `self.client.catalog_name` must equal `EARTHDATA` for any `AbstractLandsat` subclass.
- Stdlib `logging` (no `structlog` introduction).

## Acceptance Criteria (AC)

- `AbstractStacWrapper.__init__` signature includes `catalog_name: str = PLANETARY_COMPUTER`.
- All existing Sentinel wrappers initialize and produce identical search results to before (no regressions in `tests/test_planetary_computer_*`).
- `AbstractLandsat` targets the Earthdata catalog.
- Direct instantiation of `AbstractLandsat` raises `TypeError`.
- `StacSearch(EARTHDATA).s3_client is None`.

## Completion Protocol

1. All ACs met. [DONE]
2. Tests pass without regressions (9 new tests pass; 177 total pass). [DONE]
3. Code passes linting and type-checking (`ruff`, `mypy` clean). [DONE]
4. Commit work: `git commit -m "refactor: task 3 - parameterize AbstractStacWrapper catalog and add AbstractLandsat"` [DONE]
5. Update document: Mark as COMPLETE. [COMPLETE]
