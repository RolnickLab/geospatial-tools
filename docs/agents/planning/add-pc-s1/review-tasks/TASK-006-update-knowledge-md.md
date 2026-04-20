# TASK-006: Update KNOWLEDGE.md with S1 SAR domain invariants

## 1. Goal

Capture the two non-obvious S1 invariants — the uppercase/lowercase duality and the
`contains` operator requirement — in `KNOWLEDGE.md` so future sessions never rediscover them.

## 2. Context & References

- **Review findings:** Issues 5, 13 in `docs/agents/planning/add-pc-s1/review.md`
- **Upstream tasks:** TASK-001 through TASK-005 — all invariants are now decided and documented. This task persists them as tribal knowledge.
- **Key files:**
    - `docs/agents/instructions/KNOWLEDGE.md` — append new S1 section
- **Relevant skills:** `geospatial`

## 3. Subtasks

- [ ] 1. Add a new `## Sentinel-1 (SAR)` section to `KNOWLEDGE.md`.
- [ ] 2. Add entry: **`sar:polarizations` query operator must be `contains`, not `eq`.** Explanation: the STAC property is stored as a list (e.g., `["VV","VH"]`). The `eq` operator matches the whole list; `contains` matches a single element. Use `{"sar:polarizations": {"contains": "VV"}}`.
- [ ] 3. Add entry: **Asset keys vs. property values are different cases.** `PlanetaryComputerS1Band.VV == "vv"` (lowercase asset key used in `item.assets`). `PlanetaryComputerS1Polarization.VV == "VV"` (uppercase STAC property value used in queries). Using the wrong one silently returns empty results or missing assets.
- [ ] 4. Add entry: **`AbstractSentinel1` requires `@abstractmethod build_query()`** to enforce non-instantiability. `abc.ABC` alone without any abstract methods does NOT prevent direct instantiation.
- [ ] 5. Add entry: **S1 IW GRD on Planetary Computer uses collection `sentinel-1-grd`.** RTC variant is `sentinel-1-rtc` (separate collection, out of scope here). SLC is not available on PC.

## 4. Requirements & Constraints

- **Technical:** Markdown append only — no code changes.
- **Business:** Each entry must state the invariant, the gotcha (what goes wrong without it), and the fix in one sentence each.
- **Out of scope:** Documenting S2 or Copernicus knowledge (wrong section).

## 5. Acceptance Criteria

- [ ] AC-1: `KNOWLEDGE.md` contains a `## Sentinel-1 (SAR)` section.
- [ ] AC-2: Entry on `contains` operator is present with an inline example.
- [ ] AC-3: Entry on uppercase/lowercase duality is present, naming both enum types.
- [ ] AC-4: Entry on `@abstractmethod` requirement is present.
- [ ] AC-5: Entry on `sentinel-1-grd` vs `sentinel-1-rtc` collection names is present.

## 6. Testing & Validation

```bash
grep -n "Sentinel-1 (SAR)\|## Sentinel-1" docs/agents/instructions/KNOWLEDGE.md
grep -n "contains" docs/agents/instructions/KNOWLEDGE.md
grep -n "PlanetaryComputerS1Band\|PlanetaryComputerS1Polarization" docs/agents/instructions/KNOWLEDGE.md
grep -n "abstractmethod" docs/agents/instructions/KNOWLEDGE.md
grep -n "sentinel-1-rtc" docs/agents/instructions/KNOWLEDGE.md
```

Expected: each grep returns at least one match.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm each grep returns at least one match.
3. Stage and commit:
    ```bash
    git add docs/agents/instructions/KNOWLEDGE.md
    git commit -m "docs(knowledge): add S1 SAR domain invariants — closes TASK-006"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary — this is the final review task; confirm all six tasks are complete.
