# STAC Search and Download Structure

This document outlines the current structure, tools, and approaches used in `geospatial_tools` to search and download images from the Planetary Computer's STAC catalog, based on `src/geospatial_tools/stac.py` and `src/geospatial_tools/utils.py`.

## 1. Core Components

The functionality is primarily encapsulated in the `stac.py` module, which leverages `pystac` and `pystac_client` for STAC interactions.

### 1.1. Catalog Management

- **`create_planetary_computer_catalog`**: Creates a `pystac_client.Client` specifically for the Microsoft Planetary Computer API (`https://planetarycomputer.microsoft.com/api/stac/v1`). It includes retry logic and uses `planetary_computer.sign_inplace` to sign assets for access.
- **`catalog_generator`**: A factory function to retrieve a STAC client based on a catalog name. Currently, only "planetary_computer" is supported.
- **`list_available_catalogs`**: Returns the list of supported catalogs (currently just `PLANETARY_COMPUTER`).

### 1.2. Data Structures

- **`AssetSubItem`**: Represents a single downloaded file (e.g., a specific band of a satellite image). It holds the reference to the original STAC Item, the item ID, the band name, and the local filename/path.
- **`Asset`**: Represents a logical asset, which can contain multiple `AssetSubItem`s (bands). It manages:
    - `asset_id`: The ID of the STAC Item.
    - `bands`: List of bands associated with this asset.
    - `list`: A list of `AssetSubItem` objects.
    - `merged_asset_path`: Path to the merged raster file (if merged).
    - `reprojected_asset_path`: Path to the reprojected raster file (if reprojected).
    - **Methods**:
        - `add_asset_item`: Adds a sub-item.
        - `merge_asset`: Merges the downloaded bands into a single raster using `geospatial_tools.raster.merge_raster_bands`.
        - `reproject_merged_asset`: Reprojects the merged asset using `geospatial_tools.raster.reproject_raster`.
        - Cleanup methods: `delete_asset_sub_items`, `delete_merged_asset`, `delete_reprojected_asset`.

### 1.3. Search Logic (`StacSearch` Class)

The `StacSearch` class is the main entry point for searching and downloading data.

- **Initialization**: Takes a `catalog_name` and initializes the corresponding `pystac_client.Client`.
- **Search Methods**:
    - **`search`**: A wrapper around `client.search()`. It accepts standard STAC search parameters (date_range, bbox, collections, query, etc.) and handles retries.
    - **`search_for_date_ranges`**: Iterates over a list of date ranges and performs a search for each, aggregating the results. This is useful for discontinuous time periods.
- **Filtering and Sorting**:
    - **`sort_results_by_cloud_coverage`**: Sorts the search results based on the `eo:cloud_cover` property (ascending).
    - **`filter_no_data`**: Filters results based on a maximum threshold for a specific property (often used for nodata values, though the implementation checks `item.properties[property_name] < max_no_data_value`).
- **Download Methods**:
    - **`download_search_results`**: Downloads assets for *all* search results.
    - **`download_sorted_by_cloud_cover_search_results`**: Sorts results by cloud cover (if not already sorted) and downloads the top `first_x_num_of_items` (or all if not specified).
    - **`download_best_cloud_cover_result`**: Downloads only the single result with the lowest cloud cover.
    - **`_download_assets`**: Internal method that iterates through requested bands, checks availability in the STAC Item, and downloads them using `geospatial_tools.utils.download_url`.

## 2. Utilities (`utils.py`)

Helper functions used by the STAC module:

- **`download_url`**: Handles the actual HTTP GET request to download a file from a URL to a local path. It includes checks for existing files to avoid re-downloading.
- **`create_date_range_for_specific_period`**: Generates a list of ISO 8601 date range strings (e.g., "2020-03-01T00:00:00Z/2020-05-31T23:59:59Z") given start/end years and start/end months. This is used in conjunction with `search_for_date_ranges`.
- **`create_logger`**: Standard logging setup.

## 3. Workflow Summary

1. **Initialize**: Create a `StacSearch` object with "planetary_computer".
2. **Search**: Call `search()` or `search_for_date_ranges()` with criteria (collections, bbox, datetime, etc.).
3. **Process Results**:
    - Optionally sort by cloud cover (`sort_results_by_cloud_coverage`).
    - Optionally filter by other properties (`filter_no_data`).
4. **Download**: Call one of the download methods (`download_search_results`, `download_best_cloud_cover_result`, etc.) specifying the desired bands and a base directory.
    - This triggers `_download_assets`, which uses `utils.download_url`.
    - Returns `Asset` objects containing `AssetSubItem`s.
5. **Post-Processing (Optional)**:
    - Use `Asset.merge_asset()` to combine bands into a single file.
    - Use `Asset.reproject_merged_asset()` to reproject the merged file.
