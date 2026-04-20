# 1. Scope & Context

Add Sentinel-1 (S1) GRD STAC client to Planetary Computer. Sentinel-1 is SAR (active microwave):
it transmits and receives microwave pulses, making cloud cover irrelevant. Optical properties like
`max_cloud_cover`, `max_no_data_value`, and `eo:cloud_cover` do not apply. Filtering dimensions
for S1 are `sar:instrument_mode`, `sar:polarizations`, and `sat:orbit_state`.

# 2. Architectural Approach

**Files:** `src/geospatial_tools/stac/planetary_computer/constants.py` and a new
`src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.

**Class pattern — mirrors S2:**

- `Sentinel1Search` is a **state bag** (mirrors `Sentinel2Search`). It stores SAR search
    parameters and implements `build_query() -> dict`. It does NOT call `StacSearch` directly.
- `sentinel_1_search(...)` is a **standalone STAC function** (mirrors
    `sentinel_2_complete_tile_search`). It creates a `Sentinel1Search`, calls `build_query()`, and
    passes the result to `StacSearch.search_for_date_ranges()`.

**Constants — six `StrEnum` types in `constants.py`:**

| Enum                                | Values                                                        | Purpose                                           |
| ----------------------------------- | ------------------------------------------------------------- | ------------------------------------------------- |
| `PlanetaryComputerS1Collection`     | `sentinel-1-grd`                                              | Collection identifier                             |
| `PlanetaryComputerS1Property`       | `sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state` | STAC query property keys                          |
| `PlanetaryComputerS1Band`           | `vv`, `vh` (lowercase)                                        | PC asset keys — `item.assets["vv"]`               |
| `PlanetaryComputerS1InstrumentMode` | `IW`, `EW`, `SM`, `WV` (uppercase)                            | `sar:instrument_mode` property values             |
| `PlanetaryComputerS1Polarization`   | `VV`, `VH`, `HH`, `HV` (uppercase)                            | `sar:polarizations` property values               |
| `PlanetaryComputerS1OrbitState`     | `ascending`, `descending` (lowercase)                         | `sat:orbit_state` values per STAC `sat` extension |

**Key invariant:** `PlanetaryComputerS1Band` (lowercase, asset keys) and
`PlanetaryComputerS1Polarization` (uppercase, query property values) are distinct enums. Never
substitute one for the other.

**STAC query constraint:** `sar:polarizations` is stored as a list in STAC items. Use the
`contains` operator per polarization, not `eq`:

```python
{"sar:polarizations": {"contains": "VV"}}
```

# 3. Verification & Failure Modes

**Verification:**

- Unit tests for all six S1 constant enums including invariant assertion
    (`PlanetaryComputerS1Band.VV != PlanetaryComputerS1Polarization.VV`).
- Unit tests for `AbstractSentinel1` ABC enforcement (`TypeError` on direct instantiation).
- Unit tests for `Sentinel1Search.build_query()` verifying `contains` operator and `orbit_state`
    omission when `None`.
- Unit test for `sentinel_1_search()` with mocked `StacSearch`.
- Integration test: `@pytest.mark.integration`, AOI `bbox=[-122.5, 47.5, -122.0, 48.0]`,
    date range `2023-01-01/2023-01-31`. Skip with `pytest -m "not integration"`.

**Failure Modes:**

- STAC API failure — handled by `StacSearch` retry logic.
- Single-pol products (VV only) — `build_query()` iterates `polarizations`; no crash on
    `polarizations=["VV"]`. Missing asset keys logged at `WARNING` and skipped at download time.
- `sar:polarizations` query returning no results — caused by using `eq` instead of `contains`.
    Prevented by enforcing the `contains` operator constraint in `build_query()`.

# 4. Implementation Steps

1. Add all six SAR constant enums to `src/geospatial_tools/stac/planetary_computer/constants.py`.
    Export all six from `src/geospatial_tools/stac/planetary_computer/__init__.py`.
    Write failing unit tests first (TDD Red), then implement (TDD Green).
    `git commit -m "feat(stac-pc): add S1 constants for planetary computer"`

2. Create `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.
    Implement `AbstractSentinel1(ABC)` with `@abstractmethod build_query()` and SAR-typed kwargs
    (`instrument_mode`, `polarizations`, `orbit_state`, `bbox`, `intersects`). No optical fields.
    Write failing tests (TDD Red), implement (TDD Green).
    `git commit -m "feat(stac-pc): implement AbstractSentinel1 base class"`

3. Implement `Sentinel1Search(AbstractSentinel1)` with `build_query()` using `contains` per
    polarization. Implement `sentinel_1_search()` standalone function. Write unit + integration
    tests. `git commit -m "feat(stac-pc): implement Sentinel1Search and sentinel_1_search"`

4. Update `docs/agents/instructions/KNOWLEDGE.md` with S1 SAR domain invariants.
    `git commit -m "docs(knowledge): add S1 SAR domain invariants"`
