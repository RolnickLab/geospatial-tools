# TASK-03: Implement Sentinel1Search and Sentinel2Search Executable Wrappers

## Goal

Implement the concrete execution wrappers `Sentinel1Search` and `Sentinel2Search`. These classes dynamically translate their builder states into valid STAC queries and delegate asynchronous downloading to the underlying `StacSearch` client without storing redundant state.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor-s2/refactor-s2-plan.md`
- **Relevant Specs**: `docs/agents/planning/refactor-s2/refactor-s2-spec.md`
- **Existing Code**:
    - `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py`

## Subtasks

1. [ ] **(TDD) Write unit tests first** for both `Sentinel1Search` and `Sentinel2Search` `search()` and `download()` methods validating:
    - The STAC query dictionary is compiled correctly based on various permutations of builder state.
    - The `download()` method properly triggers `search()` if no results are cached.
2. [ ] Implement `Sentinel2Search.search()` and update `Sentinel1Search.search()` to:
    - Dynamically construct a STAC query dict based on instance state.
    - Execute `self.client.search(...)` using the computed query, `date_range`, `bbox`/`intersects`.
    - Return `self.search_results` (which proxies `self.client.search_results`). **Delete the existing local assignments `self.search_results = self.client.search(...)` in `Sentinel1Search.search()` at `sentinel_1.py:131`** — the proxy property replaces them.
3. [ ] Implement `Sentinel2Search.download()` and update `Sentinel1Search.download()` to:
    - Assert `base_directory` is treated strictly as `pathlib.Path`.
    - If `self.search_results` (the proxy property) is `None`, implicitly trigger `self.search()`.
    - Call `self.client.download_search_results(...)` and return `self.downloaded_assets` (the proxy property). **Delete the existing local assignment `self.downloaded_assets = self.client.download_search_results(...)` in `Sentinel1Search.download()` at `sentinel_1.py:148`** — the proxy property replaces it.
4. [ ] Avoid bare `except:` blocks; handle STAC errors explicitly.

## Requirements & Constraints

- Must use `PlanetaryComputerS1Property` and `PlanetaryComputerS2Property` for query keys to ensure correctness.
- Wrappers carry query-building state (`instrument_modes`, `polarizations`, `bbox`, `date_range`, etc.) but must NOT store execution results locally — all result access goes through the Facade proxy properties.
- Strict adherence to `pathlib.Path` in the `download` method.

## Acceptance Criteria (AC)

- [ ] AC 1: `search()` methods generate valid STAC queries and delegate to `StacSearch` without storing local state.
- [ ] AC 2: `download()` methods handle `pathlib.Path` correctly and trigger `search()` implicitly if needed.
- [ ] AC 3: No duplicated state variables exist in either wrapper.
- [ ] AC 4: Unit tests pass and `make mypy` reports zero errors.

## Testing & Validation

- **Command**: `make test`, `make mypy`
- **Success State**: Unit tests covering query dictionary construction and delegation logic pass.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Commit work: `git commit -m "feat: task 03 - implement S1 and S2 executable wrappers"`
5. [ ] Update this document: Mark as COMPLETE.
