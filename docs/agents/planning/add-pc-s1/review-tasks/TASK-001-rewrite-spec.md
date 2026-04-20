# TASK-001: Rewrite add-pc-s1-spec.md with complete SAR query semantics and architecture decision

## 1. Goal

Produce a corrected spec that (a) resolves the `sar:polarizations` query operator ambiguity,
(b) decides where search logic lives, (c) mandates three missing value enums, (d) requires spatial
filtering, and (e) pins the integration-test AOI and date window — so every downstream task has
a single unambiguous source of truth.

## 2. Context & References

- **Review findings:** Issues 1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14 in `docs/agents/planning/add-pc-s1/review.md`
- **Upstream tasks:** None — this is the root document for TASK-002 through TASK-005.
- **Key files:**
    - `docs/agents/planning/add-pc-s1/add-pc-s1-spec.md` — file to replace
    - `src/geospatial_tools/stac/planetary_computer/constants.py` — existing enum structure to mirror
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — existing class structure
    - `src/geospatial_tools/stac/core.py` — `StacSearch` interface
- **Relevant skills:** `systemdesign`, `geospatial`, `python`

## 3. Subtasks

- [ ] 1. Add §2 Functional Requirements entry for three missing value enums: `PlanetaryComputerS1InstrumentMode` (IW/EW/SM/WV), `PlanetaryComputerS1Polarization` (VV/VH/HH/HV — uppercase, STAC property values), `PlanetaryComputerS1OrbitState` (ascending/descending — lowercase, STAC `sat` extension values).
- [ ] 2. Add §2 Functional Requirements entry for spatial filtering: "`AbstractSentinel1.__init__` accepts `bbox` and `intersects` kwargs; both are passed through to `StacSearch.search()`."
- [ ] 3. Resolve architecture decision in §3 Technical Constraints: state explicitly that `Sentinel1Search` is a **state bag** (mirrors `Sentinel2Search`), and SAR STAC calls are made via a standalone function `sentinel_1_search(...)` that uses `StacSearch` directly — matching the S2 pattern.
- [ ] 4. Add §3 constraint: "`sar:polarizations` is a list property; queries must use the STAC `contains` operator per polarization, not `eq`. Example: `{"sar:polarizations": {"contains": "VV"}}`."
- [ ] 5. Add §3 constraint: "STAC property values for `sar:polarizations` are uppercase (`VV`, `VH`). PC asset keys are lowercase (`vv`, `vh`). These are distinct enums and must never be conflated."
- [ ] 6. Add §3 constraint: "Default `instrument_mode` must use `PlanetaryComputerS1InstrumentMode.IW`, not a raw string."
- [ ] 7. Add §3 constraint: "`sar:product_type` is out of scope; document as a known variant (GRDH/GRDM/GRDF) but do not filter on it."
- [ ] 8. Update §4 Acceptance Criteria to include: three value enums exist with correct values; polarization query uses `contains`; `AbstractSentinel1` cannot be instantiated directly (requires `@abstractmethod`); spatial filter kwargs accepted.
- [ ] 9. Update §7 Verification Plan integration test entry: pin AOI to `bbox=[-122.5, 47.5, -122.0, 48.0]` (Seattle region, dense S1 coverage), date range `2023-01-01/2023-01-31`, mark with `pytest.mark.integration` and document skip: `pytest -m "not integration"`.
- [ ] 10. Add §6 Out of Scope entry: "`sar:product_type` sub-variants (GRDH/GRDM/GRDF); Sentinel-1 RTC collection (`sentinel-1-rtc`); SLC data; S1 on Copernicus catalog."

## 4. Requirements & Constraints

- **Technical:** Spec is a Markdown document — no code changes in this task.
- **Business:** All downstream tasks (TASK-002 through TASK-005) must be authorable from this spec alone without referencing the old version.
- **Out of scope:** Implementation of any code. `KNOWLEDGE.md` updates (handled in TASK-005). Rewriting `add-pc-s1.md` plan (TASK-002).

## 5. Acceptance Criteria

- [ ] AC-1: Spec §2 lists `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, and `PlanetaryComputerS1OrbitState` as required functional requirements.
- [ ] AC-2: Spec §3 states the `contains` operator requirement with an inline example.
- [ ] AC-3: Spec §3 states the uppercase/lowercase invariant for property values vs. asset keys.
- [ ] AC-4: Spec §3 states `Sentinel1Search` is a state bag; SAR STAC calls go through a standalone `sentinel_1_search()` function.
- [ ] AC-5: Spec §3 states `AbstractSentinel1` requires at least one `@abstractmethod`.
- [ ] AC-6: Spec §4 AC requires spatial filter kwargs on `AbstractSentinel1`.
- [ ] AC-7: Spec §7 integration test entry has a pinned bbox, pinned date range, and `pytest.mark.integration` marker documented.
- [ ] AC-8: Spec §6 explicitly lists `sar:product_type` filtering as out of scope.

## 6. Testing & Validation

```bash
# Verify the file exists and is non-empty
wc -l docs/agents/planning/add-pc-s1/add-pc-s1-spec.md

# Grep for mandatory new content
grep -n "contains" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
grep -n "PlanetaryComputerS1InstrumentMode" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
grep -n "PlanetaryComputerS1Polarization" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
grep -n "PlanetaryComputerS1OrbitState" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
grep -n "sentinel_1_search" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
grep -n "pytest.mark.integration" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
grep -n "bbox" docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
```

Expected: each grep returns at least one match.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm each grep returns at least one match.
3. Stage and commit:
    ```bash
    git add docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
    git commit -m "docs(stac-pc): rewrite S1 spec with SAR query semantics and arch decision — closes TASK-001"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-002.
