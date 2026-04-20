# Review: add-pc-s1 Plan, Spec & Tasks

**Verdict: NEEDS WORK**

Reviewed: `add-pc-s1.md`, `add-pc-s1-spec.md`, `tasks/01-add-constants.md`, `tasks/02-abstract-sentinel1.md`, `tasks/03-sentinel1search.md`
Cross-checked against: `src/geospatial_tools/stac/planetary_computer/sentinel_2.py`, `constants.py`, `stac/core.py`

______________________________________________________________________

## Critical Issues

**1. `sar:polarizations` is a LIST — STAC query extension needs `contains`, not `eq`.**
Plan says "filters by `instrument_mode` and `polarizations`" but never specifies the operator.
`{"sar:polarizations": {"eq": ["VV","VH"]}}` will not match PC STAC items. You need per-polarization
`{"sar:polarizations": {"contains": "VV"}}` or a post-search asset-key check.
Decide and write it down. Affects Spec §4 AC and Task 3 subtask 3.

**2. `AbstractSentinel2` is not actually abstract — no `@abstractmethod`.**
It inherits `abc.ABC` but defines zero abstract methods, so `AbstractSentinel2()` instantiates fine.
If you mirror it, Task 2 AC "cannot be instantiated directly" will fail at runtime.
Either add a real `@abstractmethod` (e.g. `build_query() -> dict`) or drop the ABC façade.
Do not propagate the existing bug.

**3. No spatial filter mentioned anywhere.**
A STAC client without `bbox` / `intersects` is useless for S1. Spec and all three tasks ignore it.
Either state "spatial filtering is delegated to `StacSearch.search()` at call time" or define it as an
`AbstractSentinel1` attribute. Silence is not a design.

**4. Magic-string violation against your own NFR.**
Plan defaults `instrument_mode="IW"` and `polarizations=["VV","VH"]` as raw strings, then states "No magic strings" in NFR §2.2.
Three missing enums:

- `PlanetaryComputerS1InstrumentMode` — values: `IW`, `EW`, `SM`, `WV`
- `PlanetaryComputerS1Polarization` — values: `VV`, `VH`, `HH`, `HV` (uppercase; these are STAC property values)
- `PlanetaryComputerS1OrbitState` — values: `ascending`, `descending` (lowercase per STAC `sat` extension)

Without these, Task 1 is incomplete.

**5. Uppercase/lowercase trap not surfaced anywhere.**
STAC property `sar:polarizations` uses **uppercase** (`"VV"`, `"VH"`).
PC asset keys use **lowercase** (`"vv"`, `"vh"`).
The plan ships both cases but never states the invariant. This belongs in `KNOWLEDGE.md`
and in docstrings on both enums. The next implementer will get this wrong.

**6. Architectural ambiguity: where does search live?**
`Sentinel2Search` is a state bag; actual STAC calls happen in `sentinel_2_complete_tile_search`
against `StacSearch`. Task 3 subtask 3 hedges: *"Add `search` or equivalent querying logic …
If search logic lives elsewhere … build the equivalent `sentinel_1_search` functional wrapper."*
That is not a decision. Pick one pattern before writing code or the implementer will drift.

______________________________________________________________________

## Moderate Issues

**7. Typing gap on `polarizations`.**
Plan uses raw `list[str]`. Project mandates strict typing. Use `list[PlanetaryComputerS1Polarization] | None`.

**8. `orbit_state` default is undocumented.**
Plan says "optional" — set explicit `None` default, document it as "no filter applied".

**9. Integration test is flaky-by-design.**
"Fetch S1 GRD items and assert `sar:instrument_mode == IW`" — no fixed bbox, no fixed date range,
no `pytest.mark.integration` / network-skip marker. Pin a small AOI + known date window; mark the
test so CI can skip without a live connection.

**10. Mirroring `successful_results` / `incomplete_results` / `error_results` on the base class.**
Those state containers belong to the S2 tile-coverage workflow, not a generic SAR base class.
The spec's "base structure mimics S2" invites this waste. Do not copy them unless there is an S1 equivalent workflow.

**11. Single-pol handling is a bullet point, not a spec.**
Spec acknowledges some products lack `vh` but provides no mechanism. Specify:
"Download path iterates `polarizations`, logs `WARNING` when a requested pol is absent in `item.assets`, continues."
The pattern is already used in `core._download_assets`. Write it explicitly so the test can verify it.

**12. `sar:product_type` not addressed.**
PC `sentinel-1-grd` exposes GRDH / GRDM / GRDF variants. Either filter by `sar:product_type`
(default `GRD`) or state explicitly it is out of scope. Don't leave it ambient.

**13. `KNOWLEDGE.md` update missing from tasks.**
`docs/agents/agent_instructions.md` §4 mandates tribal-knowledge capture. The
lowercase-asset / uppercase-property split and the `contains` operator caveat for `sar:polarizations`
both belong there. Add a subtask.

**14. `PlanetaryComputerS1Collection.GRD` naming is undocumented.**
S2 uses `.L2A` (product level). S1 GRD mixes product type and level. The name is fine;
document the rationale.

**15. Commit message format inconsistent.**
Tasks specify plain commit text. Existing history uses conventional-commit scope:
`feat(stac-pc): add sentinel-1 constants for planetary computer`.

**16. Plan tone replaces rationale.**
`add-pc-s1.md` reads "Mirroring Sentinel-2 blindly is stupid." Future readers need the *why*, not the attitude.
Replace with: "Sentinel-1 is SAR (active microwave); cloud-cover and optical-nodata semantics do not apply.
Filtering dimensions are polarization, instrument mode, and orbit state."

______________________________________________________________________

## Summary

16 issue(s) found.

### Proposed fix order (one section at a time, approval between each)

1. Rewrite `add-pc-s1-spec.md` — `contains` query pattern, spatial-filter handling, three missing value enums, architecture decision, pinned integration-test AOI.
2. Rewrite `add-pc-s1.md` — reflect decided architecture, replace attitude with rationale.
3. Rewrite `tasks/01-add-constants.md` — add three missing value enums, document asset-key vs. property-value invariant.
4. Rewrite `tasks/02-abstract-sentinel1.md` — real `@abstractmethod`, typed polarizations, drop S2 state containers.
5. Rewrite `tasks/03-sentinel1search.md` — pinned search architecture, single-pol handling, deterministic integration test with marker.
