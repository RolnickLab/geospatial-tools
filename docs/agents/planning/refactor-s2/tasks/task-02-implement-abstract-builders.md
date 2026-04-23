# TASK-02: Implement Abstract Builders (Facade + Proxy Pattern)

## Goal

Refactor both `AbstractSentinel1` and `AbstractSentinel2` into strict Abstract Base Classes (`abc.ABC`) providing a fluent builder pattern. They must act as pure Facades over `StacSearch`, managing query state while delegating execution and result storage exclusively to the underlying client via `@property` proxies.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor-s2/refactor-s2-plan.md`
- **Relevant Specs**: `docs/agents/planning/refactor-s2/refactor-s2-spec.md`
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py`

## Subtasks

1. [ ] **(TDD) Define interface contract first**: write the method signatures and docstrings for `_invalidate_state`, proxy properties, and builder methods before implementing. Then write **failing unit test stubs** for both `AbstractSentinel1` and `AbstractSentinel2` validating:
    - Instantiation failure (`TypeError`) — requires at least one `@abstractmethod` per `KNOWLEDGE.md`.
    - Builder methods mutate instance query state AND set `self.client.search_results = None` and `self.client.downloaded_search_assets = None`.
        Tests will remain failing (red) until subtasks 5–7 are complete.
2. [ ] Ensure `AbstractSentinel1` and `AbstractSentinel2` inherit from `abc.ABC`.
3. [ ] Redefine `AbstractSentinel2.__init__` to accept spatial kwargs (`bbox`, `intersects`) and exactly one `date_range: DateLike`, matching the `AbstractSentinel1` signature.
4. [ ] Instantiate `self.client = StacSearch(PLANETARY_COMPUTER)` within `__init__` for both classes.
5. [ ] Remove duplicated state properties (`search_results`, `downloaded_assets`) from `AbstractSentinel1`'s `__init__`.
6. [ ] Implement `@property` proxies for `search_results` and `downloaded_assets` in both base classes, delegating to `self.client.search_results` and `self.client.downloaded_search_assets` respectively. Do NOT store duplicate state.
7. [ ] Implement a `_invalidate_state(self) -> None` method in both base classes that sets `self.client.search_results = None` and `self.client.downloaded_search_assets = None`.
8. [ ] Ensure all fluent builder methods in both classes return `typing.Self` and explicitly call `self._invalidate_state()` before returning to prevent stale state:
    - Sentinel-1: `filter_by_instrument_mode`, `filter_by_polarization`, `filter_by_orbit_state`, `with_custom_query`
    - Sentinel-2: `filter_by_cloud_cover`, `filter_by_nodata_pixel_percentage`, `filter_by_mgrs_tile`, `with_custom_query`

## Requirements & Constraints

- Must use `typing.Self` for precise type hinting.
- Base classes must not execute any STAC searches or store duplicate result states.

## Acceptance Criteria (AC)

- [ ] AC 1: Both abstract classes cannot be instantiated.
- [ ] AC 2: `search_results` and `downloaded_assets` correctly proxy the underlying `StacSearch` state in both S1 and S2 wrappers.
- [ ] AC 3: Calling any builder method explicitly invalidates the underlying `StacSearch` cached results.
- [ ] AC 4: Unit tests pass and `make mypy` reports zero errors.

## Testing & Validation

- **Command**: `make test`, `make mypy`
- **Success State**: Unit tests pass. Static typing passes.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Commit work: `git commit -m "feat: task 02 - implement Abstract Builders with Facade proxy pattern"`
5. [ ] Update this document: Mark as COMPLETE.
