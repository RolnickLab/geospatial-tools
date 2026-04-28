# SPEC: Planetary Computer Sentinel-1 & Sentinel-2 Facade Pattern Refactor

## 1. Overview

- **Goal**: Refactor both Sentinel-1 and Sentinel-2 STAC wrappers (`AbstractSentinel1`, `Sentinel1Search`, `AbstractSentinel2`, `Sentinel2Search`) to implement a strict **Facade + Proxy property pattern**. Decouple the legacy `BestProductsForFeatures` orchestrator from the S2 base class to preserve its functionality while enabling the refactor.
- **Problem Statement**: The Sentinel-2 classes are prototypical and lack a builder API. The Sentinel-1 classes have a builder API but duplicate execution state (`search_results`), leading to potential silent data bugs if filters are modified post-search. Both sets of wrappers violate Clean Architecture principles regarding single responsibility and low coupling.
- **Design intent (scope lock)**: Establish thin, synchronous wrappers for STAC query generation on optical and radar data. Base classes must act as pure Facades, delegating all state storage (`search_results`, `downloaded_assets`) and execution to a composed `StacSearch` client. Strict typing (`typing.Self`) and idiomatic Python (e.g., `pathlib.Path`) must be enforced.

## 2. Requirements

### Functional Requirements

- [ ] Isolate `BestProductsForFeatures` by removing its inheritance from `AbstractSentinel2`. Remove the `super().__init__(...)` call. Move legacy state (`date_ranges`, `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`, `error_results`) and the `create_date_ranges` method directly into it.
- [ ] Refactor `AbstractSentinel1` and `AbstractSentinel2` into `abc.ABC` classes that cannot be instantiated directly.
- [ ] Base class `__init__` methods must instantiate an internal `StacSearch(PLANETARY_COMPUTER)` as `self.client`.
- [ ] Base classes must expose `@property` proxies for `search_results` and `downloaded_assets` that point to `self.client.search_results` and `self.client.downloaded_search_assets` respectively. They must NOT store duplicate local state.
- [ ] Base classes must implement `_invalidate_state(self) -> None` that sets `self.client.search_results = None` and `self.client.downloaded_search_assets = None`.
- [ ] All builder methods in `AbstractSentinel1` (e.g., `filter_by_polarization`) and `AbstractSentinel2` (e.g., `filter_by_cloud_cover`) must return `typing.Self` for precise type hinting and MUST call `self._invalidate_state()` before returning.
- [ ] Implement `Sentinel1Search` and `Sentinel2Search` with `search()` and `download()` methods.
- [ ] `search()` must dynamically construct the STAC `query` dictionary, merge `custom_query_params`, execute `self.client.search(...)`, and return the proxy `self.search_results`. The methods must be idempotent.
- [ ] `download(..., base_directory: pathlib.Path | str)` triggers `self.search()` if the proxy `search_results` is `None`, calls `self.client.download_search_results(...)`, and returns the proxy `self.downloaded_assets`. The `base_directory` must be strictly typed and handled as `pathlib.Path`.

### Non-Functional Requirements

- **Consistency**: Both S1 and S2 APIs must exactly mirror each other using the Facade pattern, providing a unified developer experience.
- **Type Safety**: Use `StrEnum` for all domain constants. Spatial kwargs typed as `geotools_types.BBoxLike` / `geotools_types.IntersectsLike`. Use strict type hints (`typing.Self`, specific return types).
- **Backward Compatibility**: `BestProductsForFeatures` and its module-level functions must continue to function exactly as before without modification to their internal logic.
- **Code Quality**: Code must pass `make mypy`, `make pylint`, `make precommit`, and existing `make test` checks. Do not use bare `except` blocks; target specific errors (e.g. `pystac.StacError`).

## 3. Technical Constraints & Assumptions

- **Architecture Decision**: The wrappers own a `StacSearch` instance via composition. Query-building state (filters, spatial params, date range) lives on the wrapper. Execution results are stored exclusively on `self.client` (`search_results`, `downloaded_search_assets` — both plain settable attributes on `StacSearch`). Mutating query state must call `_invalidate_state()` to nil out those client attributes and prevent stale-result access.
- **Legacy Orchestrator**: `BestProductsForFeatures` acts as a standalone orchestrator. Isolating it is a prerequisite to cleanly refactoring `Sentinel2Search`.
- **PC STAC Validation**: Specific query parameter formatting for optical vs radar properties must align with `pystac_client` operators (`lt`, `in`, `eq`).

## 4. Acceptance Criteria

- [ ] `BestProductsForFeatures` no longer inherits from `AbstractSentinel2`, contains no `super()` call, and retains all required state/methods internally.
- [ ] `AbstractSentinel1` and `AbstractSentinel2` implement the Facade + Proxy pattern with proper state invalidation on mutation.
- [ ] `Sentinel1Search` and `Sentinel2Search` dynamically build queries and delegate execution to `self.client` without duplicating state.
- [ ] Unit and live integration tests pass for both S1 and S2 wrappers.
- [ ] The codebase passes all project QA pipelines (`make pylint`, `make mypy`, `make precommit`, `make test`).

## 5. Dependencies

- Planetary Computer STAC API.
- `geospatial_tools.stac.core.StacSearch`, `Asset`, `PLANETARY_COMPUTER`.
- `geospatial_tools.geotools_types.BBoxLike`, `IntersectsLike`, `DateLike`.
- `geospatial_tools.stac.planetary_computer.constants.*`

## 6. Out of Scope

- Refactoring the internal logic of `BestProductsForFeatures` or its associated helper functions.
- Migrating `BestProductsForFeatures` to use the new `Sentinel2Search` builder pattern.

## 7. Verification Plan

- **QA Pipeline**: Run `make precommit`, `make pylint`, and `make mypy` to enforce type safety and code quality standards.
- **Unit Testing**:
    - Verify base class instantiation raises `TypeError`.
    - Verify builder methods mutate query state AND invalidate client state.
    - Verify executable methods trigger searches correctly and generate proper query dictionaries.
- **Integration Testing**:
    - `@pytest.mark.integration` tests pinning a specific bounding box and date range for both S1 and S2.
    - Chain builder methods.
    - Assert results are returned and possess the expected properties.
    - Verify that existing legacy tests for `BestProductsForFeatures` still pass.
