# 1. 🎯 Scope & Context

Add Sentinel-1 (S1) GRD STAC client. Mirroring Sentinel-2 blindly is stupid; S1 is SAR. SAR penetrates clouds. `max_cloud_cover` is garbage here. Need S1-specific abstractions.

# 2. 🏗️ Architectural Approach

Create `AbstractSentinel1` and `Sentinel1Search` in `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`. Do NOT copy optical properties. S1 requires `sar:instrument_mode` (default `IW`), `sar:polarizations` (e.g., `VV`, `VH`), and `sat:orbit_state` (ascending/descending).
Use `StrEnum` in `constants.py` for `PlanetaryComputerS1Collection` (`sentinel-1-grd`), `PlanetaryComputerS1Property` (`sar:instrument_mode`, `sar:polarizations`, `sat:orbit_state`), and `PlanetaryComputerS1Band` (`vv`, `vh` - MUST be lowercase per PC STAC spec).

# 3. 🛡️ Verification & FMEA

**Verification:**

- Unit tests for S1 constants.
- Unit tests for `Sentinel1Search` init checking SAR-specific kwargs.
- Integration test for PC STAC S1 GRD products.

**Failure Modes:**

- STAC API failure. Handled by `StacSearch`.
- Polarization mismatch. Some S1 products are single pol (VV only). Code must handle missing `vh` asset without crashing.
- Invalid CRS. Handled by `geospatial_tools`.

# 4. 📝 Implementation Steps

1. Add SAR constants to `src/geospatial_tools/stac/planetary_computer/constants.py` (`vv`, `vh`, `sar:instrument_mode`, `sat:orbit_state`, `sar:polarizations`).
2. Create `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.
3. Implement `AbstractSentinel1` with `instrument_mode`, `polarizations`, `orbit_state` kwargs. Drop optical kwargs.
4. Implement `Sentinel1Search` handling STAC queries for SAR parameters.
5. Create `tests/test_planetary_computer_sentinel1.py`.

# 5. 🔄 Next Step

Do you approve Step 1?
