---
name: KNOWLEDGE
description: Project Knowledge Base
---
# Project Knowledge Base

## STAC Catalogs

- **Planetary Computer (PC):** Primary data source. Uses `planetary-computer` library for `sign_inplace` modifier.
- **Copernicus Data Space Ecosystem (CDSE):** Added in Feb 2026.
    - STAC API: `https://catalogue.dataspace.copernicus.eu/stac`
    - Auth: OIDC Bearer token required for asset downloads.
    - Collection IDs: `sentinel-2-l2a`, `sentinel-1-slc`, etc.
    - Implementation: `src/geospatial_tools/copernicus.py`

## Known Issues & Fixes

- **stac.py Bug (Fixed):** `CATALOG_NAME_LIST` was incorrectly initialized from a string (`frozenset("abc")` -> `{'a', 'b', 'c'}`). Fixed to use a list (`frozenset(["abc"])`).

## Makefile

The project uses a makefile. Use 'make targets' to discover the targets.

## QA

- Use 'make precommit', 'make pylint' and 'make test' to validate code.

## Sentinel-1 (SAR)

- **`sar:polarizations` query operator must be `contains`, not `eq`.**
  The STAC property is stored as a list (e.g., `["VV","VH"]`). Using `eq` matches the whole list
  and returns no results for partial matches. Use `contains` per polarization:
  `{"sar:polarizations": {"contains": "VV"}}`.

- **Asset keys and property values are different cases — never substitute one for the other.**
  `PlanetaryComputerS1Band.VV == "vv"` (lowercase) is used as `item.assets["vv"]`.
  `PlanetaryComputerS1Polarization.VV == "VV"` (uppercase) is used in STAC query property values.
  Using the wrong one silently returns empty results or causes missing-asset errors.

- **`abc.ABC` alone does NOT prevent direct instantiation — `@abstractmethod` is required.**
  `AbstractSentinel1` (and `AbstractSentinel2`) must define at least one `@abstractmethod` (e.g.
  `build_query()`) for `TypeError` to be raised on direct instantiation. An empty ABC subclass is
  fully instantiable.

- **Planetary Computer S1 collection names.**
  Standard GRD: `sentinel-1-grd` (`PlanetaryComputerS1Collection.GRD`).
  RTC (Radiometric Terrain Corrected): `sentinel-1-rtc` — separate collection, not covered by the
  current S1 client. SLC is not available on Planetary Computer.
