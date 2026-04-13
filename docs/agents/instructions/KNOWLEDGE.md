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
