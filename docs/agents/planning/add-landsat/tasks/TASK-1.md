# TASK-1: Update stac/core.py for Earthdata STAC

## Goal

Add NASA Earthdata STAC Catalog endpoint and catalog creation logic to core STAC module.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md

## Subtasks

1. Add `EARTHDATA = "earthdata"` to catalog names in `stac/core.py`.
2. Add `EARTHDATA_API = "https://cmr.earthdata.nasa.gov/stac/"` in `stac/core.py`.
3. Update `CATALOG_NAME_LIST` to include `EARTHDATA`.
4. Implement `create_earthdata_catalog(max_retries, delay, logger)` reusing retry/backoff pattern. Catalog client is anonymous.
5. Register factory in `catalog_generator()` dispatch dict (`EARTHDATA: create_earthdata_catalog`).
6. Add unit tests in `test_stac_core.py` verifying connection and retry behavior.

## Requirements & Constraints

- Handle connection errors gracefully via existing retry pattern.
- Do not break existing Planetary Computer or Copernicus functionality.
- Scope is search-side wiring only. Download-path auth is TASK-6.

## Acceptance Criteria (AC)

- `EARTHDATA` present in `CATALOG_NAME_LIST` and reported by `list_available_catalogs()`.
- `catalog_generator(EARTHDATA)` returns configured `pystac_client.Client`.
- Retries logged and handled correctly when `pystac_client.Client.open` fails.

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "feat: task 1 - add Earthdata STAC catalog to core"`
5. Update document: Mark as COMPLETE.
