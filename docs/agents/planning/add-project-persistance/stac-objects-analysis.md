# STAC Objects Analysis: Asset and AssetSubItem

This document analyzes how STAC (SpatioTemporal Asset Catalog) searches are represented and utilized within the `geospatial_tools` repository, specifically focusing on the `Asset` and `AssetSubItem` classes.

## Representation of STAC Searches

The STAC API interactions are managed primarily through the `StacSearch` class in `src/geospatial_tools/stac.py`. When a search is performed and assets are downloaded, the results are represented using the `Asset` and `AssetSubItem` classes.

### AssetSubItem

The `AssetSubItem` class represents a single component of a STAC asset. In the context of satellite imagery, this generally corresponds to a single spectral band (e.g., Red, Green, Near-Infrared).

Key attributes of `AssetSubItem` include:

- `asset`: The original `pystac.Item` reference.
- `item_id`: The unique identifier for the STAC item.
- `band`: The specific band name (e.g., `B04`).
- `filename`: The local `pathlib.Path` to the downloaded file for this specific band.

### Asset

The `Asset` class represents a complete STAC product or scene, which is typically composed of multiple individual bands. It acts as a container and a manager for multiple `AssetSubItem` instances.

Key features and responsibilities of `Asset` include:

- **Aggregation**: It maintains a list (`self.list`) of `AssetSubItem` objects that belong to the same product.
- **Processing**: It provides methods to perform operations on the aggregated sub-items, such as merging multiple individual bands into a single multi-band raster file (`merge_asset()`).
- **Reprojection**: It includes methods to reproject the merged raster into a different Coordinate Reference System (CRS) (`reproject_merged_asset()`).
- **Lifecycle Management**: It provides utility methods to clean up intermediate files (`delete_asset_sub_items()`, `delete_merged_asset()`, `delete_reprojected_asset()`).

## Usage in the Repository

The `Asset` and `AssetSubItem` classes are central to the data acquisition and initial preprocessing pipelines.

### StacSearch Integration

In `src/geospatial_tools/stac.py`, the `StacSearch` class orchestrates the downloading of search results. Methods like `download_search_results`, `download_sorted_by_cloud_cover_search_results`, and `download_best_cloud_cover_result` iterate through `pystac.Item` results. For each requested band, they download the file, instantiate an `AssetSubItem`, and group them into an `Asset` object.

### Sentinel-2 Product Pipeline

In `src/geospatial_tools/planetary_computer/sentinel_2.py`, the `download_sentinel2_product` function heavily relies on the `Asset` class to manage the end-to-end flow of a Sentinel-2 image:

1. **Instantiation**: An `Asset` is either returned from `stac_client.download_search_results` or instantiated directly if the processed files (merged or reprojected) already exist locally.
2. **Merging**: `asset.merge_asset()` is called to combine the individual downloaded bands into a single `.tif` file.
3. **Reprojecting**: `asset.reproject_merged_asset()` is subsequently called if a target projection is specified.
4. **Cleanup**: The parameters `delete_sub_items` and `delete_merged_asset` map to `Asset` methods to automatically delete the intermediate single-band files and the unprojected merged file once they are no longer needed.

### Notebook Exploration

The classes are also used interactively in Jupyter Notebooks (e.g., `planetary_computer_sentinel2_exploration.ipynb`). Users instantiate `Asset` objects manually for convenience when exploring downloaded products or analyzing metadata directly within the notebook environment.
