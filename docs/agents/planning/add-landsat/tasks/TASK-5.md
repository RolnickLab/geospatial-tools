# TASK-5: Live CMR USGS_EROS Integration Tests (Search Only)

Maps to **Plan Step 5**. Depends on **TASK-4**.

## Goal

Verify `Landsat8Search` and `Landsat9Search` produce real items against the live CMR STAC USGS_EROS endpoint, without patching, without downloading asset bytes.

## Context & References

- **Source Plan:** `docs/agents/planning/add-landsat/add-landsat-plan.md` (§3, §4 step 5)
- **Spec:** `docs/agents/planning/add-landsat/add-landsat-spec.md` (§7)
- **Endpoint:** `https://cmr.earthdata.nasa.gov/stac/USGS_EROS/`

## Subtasks

1. Create `tests/test_earthdata_landsat_integration.py`.
2. Write `test_landsat8_search_returns_items_from_cmr_usgs_eros`:
    - Construct `Landsat8Search` with a small bbox (e.g. CONUS sub-region) and a recent date range (e.g. last 90 days).
    - Call `.search()`.
    - Assert at least one item returned.
    - Assert `item.properties["platform"] == "LANDSAT_8"` for every returned item.
    - Assert `item.collection_id == "Landsat Level-1 Collection 2_Collection 2"` (or equivalent attribute access).
    - Assert each item has the expected asset keys (matches `EarthdataLandsatBand` enum from TASK-2).
3. Write `test_landsat9_search_returns_items_from_cmr_usgs_eros` analogously with `LANDSAT_9`.
4. Mark all tests with `@pytest.mark.integration`.

## Requirements & Constraints

- Tests use live network calls against `https://cmr.earthdata.nasa.gov/stac/USGS_EROS/`.
- Do NOT patch or mock `StacSearch`, `pystac_client`, or `requests`.
- Do NOT download asset bytes — search results metadata only.
- Skip cleanly if the endpoint is unreachable (raise → fail; pytest's normal network-failure semantics suffice — no manual `skipif` needed).

## Acceptance Criteria (AC)

- Live search returns actual items from CMR USGS_EROS.
- Asset keys match the constants defined in TASK-2.
- `platform` property strictly enforced for both 8 and 9.
- All new tests carry the `@pytest.mark.integration` marker (registered in TASK-0).

## Completion Protocol

1. All ACs met.
2. Tests pass without regressions.
3. Code passes linting and type-checking.
4. Commit work: `git commit -m "test: task 5 - add CMR USGS_EROS Landsat integration tests"`
5. Update document: Mark as COMPLETE.
