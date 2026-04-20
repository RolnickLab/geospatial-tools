# TASK-002: Rewrite add-pc-s1.md plan with rationale and decided architecture

## 1. Goal

Replace the current plan's attitude-driven prose with technical rationale, and reflect the
architecture decision from TASK-001 (state-bag class + standalone function pattern).

## 2. Context & References

- **Review findings:** Issues 6, 15, 16 in `docs/agents/planning/add-pc-s1/review.md`
- **Upstream tasks:** TASK-001 — architecture decision (state-bag + `sentinel_1_search()`) must be reflected here.
- **Key files:**
    - `docs/agents/planning/add-pc-s1/add-pc-s1.md` — file to replace
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — `sentinel_2_complete_tile_search` pattern to mirror
- **Relevant skills:** `systemdesign`

## 3. Subtasks

- [ ] 1. Replace §1 Scope & Context opening sentence ("Mirroring Sentinel-2 blindly is stupid") with: "Sentinel-1 is SAR (active microwave). Cloud cover and optical-nodata semantics do not apply. Filtering dimensions are polarization, instrument mode, and orbit state."
- [ ] 2. Update §2 Architectural Approach: state that `Sentinel1Search` is a state bag (mirrors `Sentinel2Search`); SAR STAC calls go through a standalone function `sentinel_1_search(tile_id, collection, date_ranges, instrument_mode, polarizations, orbit_state, bbox)` using `StacSearch` — matching the `sentinel_2_complete_tile_search` pattern.
- [ ] 3. Update §2 to include all five enums: `PlanetaryComputerS1Collection`, `PlanetaryComputerS1Property`, `PlanetaryComputerS1Band`, `PlanetaryComputerS1InstrumentMode`, `PlanetaryComputerS1Polarization`, `PlanetaryComputerS1OrbitState`.
- [ ] 4. Update §4 Implementation Steps to include: (a) three new value enums in constants, (b) `@abstractmethod build_query()` on `AbstractSentinel1`, (c) `sentinel_1_search()` standalone function.
- [ ] 5. Update §3 Verification to add: integration test marker (`pytest.mark.integration`), pinned AOI, pinned date range.
- [ ] 6. Update conventional-commit format in §4 steps to use scoped messages: `feat(stac-pc): ...`.

## 4. Requirements & Constraints

- **Technical:** Markdown document only — no code changes.
- **Business:** Plan must be coherent with TASK-001 spec. Any contradiction between plan and spec means spec wins.
- **Out of scope:** Code implementation. `KNOWLEDGE.md` (TASK-005).

## 5. Acceptance Criteria

- [ ] AC-1: Plan §1 replaces dismissive language with SAR domain rationale (microwave, no cloud cover).
- [ ] AC-2: Plan §2 names all six enum types (three original + three new).
- [ ] AC-3: Plan §2 explicitly describes `Sentinel1Search` as a state bag and names `sentinel_1_search()` as the standalone STAC function.
- [ ] AC-4: Plan §4 steps include `@abstractmethod` addition and `sentinel_1_search()` implementation.
- [ ] AC-5: Commit message examples in plan use scoped conventional-commit format.

## 6. Testing & Validation

```bash
# Verify mandatory content
grep -n "microwave\|active microwave" docs/agents/planning/add-pc-s1/add-pc-s1.md
grep -n "sentinel_1_search" docs/agents/planning/add-pc-s1/add-pc-s1.md
grep -n "PlanetaryComputerS1InstrumentMode\|PlanetaryComputerS1Polarization\|PlanetaryComputerS1OrbitState" docs/agents/planning/add-pc-s1/add-pc-s1.md
grep -n "abstractmethod\|@abstractmethod" docs/agents/planning/add-pc-s1/add-pc-s1.md
grep -n "feat(stac-pc)" docs/agents/planning/add-pc-s1/add-pc-s1.md
```

Expected: each grep returns at least one match.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm each grep returns at least one match.
3. Stage and commit:
    ```bash
    git add docs/agents/planning/add-pc-s1/add-pc-s1.md
    git commit -m "docs(stac-pc): rewrite S1 plan with rationale and arch decision — closes TASK-002"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-003.
