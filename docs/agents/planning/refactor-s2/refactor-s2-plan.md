# 🎯 Scope & Context

The current `AbstractSentinel2` and `Sentinel2Search` classes inside `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` are prototypical, mixing generic STAC querying with specific tiling coverage logic (`BestProductsForFeatures`). We need to refactor these into a thin, synchronous wrapper using a fluent builder pattern.
Simultaneously, `AbstractSentinel1` and `Sentinel1Search` in `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` already use a builder pattern but suffer from duplicated state management (storing `search_results` and `downloaded_assets` locally instead of delegating to the `StacSearch` client).
To align with the project's strict Python, System Design, and QA guidelines, we will refactor both Sentinel-1 and Sentinel-2 classes to use a strict **Facade + Proxy property pattern**. This provides a clean API while ensuring zero state duplication and strict invalidation of stale cache data.

# 🏗️ Architectural Approach

1. **Decouple Tiling Orchestrator**: Sever the inheritance between `BestProductsForFeatures` and `AbstractSentinel2`, making `BestProductsForFeatures` a standalone orchestrator. This enforces the "Composition over Inheritance" principle.
2. **Facade Builder Bases (`AbstractSentinel1`, `AbstractSentinel2`)**: Refactor both base classes to act as pure Facades over `StacSearch`. They will use `@property` proxies to expose `search_results` and `downloaded_assets` from the underlying client, storing NO duplicate state. All builder methods (e.g., `filter_by_cloud_cover`, `filter_by_polarization`) will return `typing.Self` and explicitly call an `_invalidate_state()` method to wipe the client's cache whenever query parameters change.
3. **Execution Wrappers (`Sentinel1Search`, `Sentinel2Search`)**: Update the concrete wrappers to dynamically construct the STAC query dict during `search()`, pass it to the proxy client, and rely on the proxy properties for `download()`. Paths in `download()` must strictly use `pathlib.Path`.
4. **Idempotency & Reliability**: Ensure that running `search()` or `download()` multiple times yields consistent results without duplicating state (e.g., clearing the query dictionary on each `search()` call). Do not use bare `except:` blocks; handle specific STAC/network exceptions explicitly.

# 🛡️ Verification & FMEA

- **Verification**:
    - Run the project QA tools (`make test`, `make mypy`, `make pylint`, `make precommit`) before and after the refactor to ensure no regressions and strict type compliance.
    - Unit tests verifying builder state mutations and successful invalidation of client state for both S1 and S2.
    - Pinned integration tests (`@pytest.mark.integration`) for both S1 and S2 on the PC STAC API.
- **Failure Modes**:
    - Regressions in `BestProductsForFeatures` or `find_best_product_per_s2_tile` due to shared dependencies. Mitigation: explicitly isolate these legacy components during refactoring and run all related tests.
    - Silent failures during STAC queries. Mitigation: Log explicit error messages using `structlog` (or existing `logger`) and avoid generic `except Exception: pass`.

# 📝 Implementation Steps

1. **Isolate Legacy Code**: Isolate `BestProductsForFeatures` from `AbstractSentinel2`. Ensure `mypy` and `make test` still pass.
2. **Implement Facade Bases**: Update `AbstractSentinel1` and `AbstractSentinel2` to the Facade + Proxy pattern. Use strict `typing.Self`.
3. **Implement Executable Wrappers**: Update `Sentinel1Search` and `Sentinel2Search` to rely purely on proxy states and correctly map builder states to STAC queries.
4. **Testing & QA**: Write/update unit tests and integration tests for both modules. Run `make pylint`, `make mypy`, `make precommit`, and `make test` to confirm compliance.
