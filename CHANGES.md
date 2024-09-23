# CHANGES.md

[Unreleased](https://github.com/RolnickLab/geospatial-tools/tree/main) (latest)
-------------------------------------------------------------------------------------

[//]: # (New changes here in list form)

[0.1.2](https://github.com/RolnickLab/geospatial-tools/tree/0.1.2) (2024-09-23)
-------------------------------------------------------------------------------------

- Fix `docformatter` with missing extra dependency for use with `pyproject.toml`


[0.1.1](https://github.com/RolnickLab/geospatial-tools/tree/0.1.1) (2024-09-20)
-------------------------------------------------------------------------------------

- Fix `black` dependency that was not correctly setup in dev dependency group

[0.1.0](https://github.com/RolnickLab/geospatial-tools/tree/0.1.0) (2024-09-20)
-------------------------------------------------------------------------------------
	
- Add `resample_tiff_raster.py` script
- Implement functions for clipping and reprojecting raster images
- Implement vector functions for grid creation
- Implement vector functions for spatial selection and spatial joins
- Implement functions to help manage and automate `pystac` API and client
- Implement functions and scripts to search for and process Sentinel 2 products from
  Microsoft's Planetary Computer
- Add examples of the above in Jupyter notebook formats
- Add tests and notebook tests