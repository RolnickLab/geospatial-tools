# TASK-1: Update `stac/core.py` for CMR Earthdata STAC (USGS_EROS provider)

Maps to **Plan Step 1**. Depends on **TASK-0**.

## Goal

Add CMR STAC Catalog (`USGS_EROS` provider scope) endpoint and catalog creation logic to the core STAC module.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§2, §2.1, §4 step 1)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§2, §3)
- **Code:** `src/geospatial_tools/stac/core.py` (existing `create_planetary_computer_catalog`, `create_copernicus_catalog`, `catalog_generator`).

## Subtasks

1. Add constants in `stac/core.py`:
    - `EARTHDATA = "earthdata"`
    - `EARTHDATA_API = "https://cmr.earthdata.nasa.gov/stac/USGS_EROS/"` (provider-scoped — the bare `/stac/` root only lists providers and is not a usable item-search endpoint for our needs).
2. Update `CATALOG_NAME_LIST` to include `EARTHDATA`.
3. Implement `create_earthdata_catalog(max_retries: int = 3, delay: int = 5, logger: logging.Logger = LOGGER) -> pystac_client.Client | None` reusing the retry/backoff structure of `create_copernicus_catalog`. Call `pystac_client.Client.open(EARTHDATA_API)`. Catalog client is anonymous (no `modifier`, no auth header).
4. Register the factory in `catalog_generator()` dispatch dict: `EARTHDATA: create_earthdata_catalog`.
5. Add unit tests in `tests/test_stac.py` (existing file) verifying:
    - `EARTHDATA in CATALOG_NAME_LIST` and `list_available_catalogs()` returns it.
    - `catalog_generator(EARTHDATA)` returns a `pystac_client.Client` (mock `pystac_client.Client.open` via `monkeypatch.setattr` to avoid network — match the existing `test_stac.py` style).
    - Retry behavior: `monkeypatch` `pystac_client.Client.open` to raise twice then succeed; assert call count and final return value.

## Requirements & Constraints

- Handle connection errors gracefully via the existing retry pattern (3 attempts, 5 s delay).
- Do not break existing Planetary Computer or Copernicus functionality.
- Scope is search-side wiring only. Download-path auth is TASK-6.
- Use `pystac_client.Client.open` only (no provider auto-discovery walks).

## Acceptance Criteria (AC)

- `EARTHDATA` present in `CATALOG_NAME_LIST` and reported by `list_available_catalogs()`.
- `catalog_generator(EARTHDATA)` returns a configured `pystac_client.Client`.
- Retries logged and handled correctly when `pystac_client.Client.open` raises.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 1 - add CMR Earthdata STAC catalog (USGS_EROS scope) to core"`
5. Update document: Mark as COMPLETE.
