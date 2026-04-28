# TASK-1: Update stac/core.py for USGS STAC

## Goal

Add the USGS STAC Catalog endpoint and catalog creation logic to the core STAC module so that it can be used by the new Landsat wrappers.

## Context & References

- **Source Plan**: docs/agents/planning/add-landsat/add-landsat-plan.md
- **Relevant Specs**: docs/agents/planning/add-landsat/add-landsat-spec.md
- **Existing Code**: `src/geospatial_tools/stac/core.py`, `tests/test_stac_core.py`

## Subtasks

1. [ ] Add `USGS = "usgs"` to catalog names in `stac/core.py`.
2. [ ] Add `USGS_API = "https://landsatlook.usgs.gov/stac-server"` in `stac/core.py`.
3. [ ] Update `CATALOG_NAME_LIST` to include `USGS`.
4. [ ] Implement `create_usgs_catalog(max_retries, delay, logger)` reusing the retry/backoff pattern from `create_planetary_computer_catalog`. **No `usgs/auth.py` module is required** — verified anonymous access (see plan §2.1).
5. [ ] Register the factory in the `catalog_generator()` dispatch dict at `core.py:109` (`USGS: create_usgs_catalog`). Without this wire-up, `StacSearch(USGS)` returns `None` and downstream Landsat searches fail silently.
6. [ ] Confirm `StacSearch._download_assets` (`core.py:730`) requires no new branch: USGS hrefs flow through the default `method = "http"` path. End-to-end proof is deferred to TASK-5 (download verification gate).
7. [ ] Add unit tests in `test_stac_core.py` verifying `create_usgs_catalog` connection, retry behavior, and that `catalog_generator(USGS)` returns a configured client.

## Requirements & Constraints

- Must handle connection errors gracefully via the existing retry pattern.
- Must not break existing Planetary Computer or Copernicus functionality.
- Must not introduce a new auth module or any branch in `_download_assets` (verified — see plan §2.1).

## Acceptance Criteria (AC)

- [ ] `USGS` is present in `CATALOG_NAME_LIST` and reported by `list_available_catalogs()`.
- [ ] `catalog_generator(USGS)` returns a configured `pystac_client.Client` (not `None`).
- [ ] Retries are logged and handled correctly when `pystac_client.Client.open` fails.
- [ ] No new file under `src/geospatial_tools/stac/usgs/auth.py`; no new branch added to `StacSearch._download_assets`.

## Testing & Validation

- **Command**: `make test` and `pytest tests/test_stac_core.py`
- **Success State**: All core STAC tests pass, including the new USGS tests.
- **Manual Verification**: Run `make precommit`, `make pylint`, `make mypy` to ensure style and types are correct.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: task 1 - add USGS STAC catalog to core"`
6. [ ] Update this document: Mark as COMPLETE.
