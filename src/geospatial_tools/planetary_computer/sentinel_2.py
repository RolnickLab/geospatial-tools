import json
import logging
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

from geopandas import GeoDataFrame

from geospatial_tools import DATA_DIR
from geospatial_tools.stac import PLANETARY_COMPUTER, Asset, StacSearch
from geospatial_tools.utils import create_date_range_for_specific_period, create_logger
from geospatial_tools.vector import spatial_join_within

LOGGER = create_logger(__name__)


class BestProductsForFeatures:
    """
    Class made to facilitate and automate searching for Sentinel 2 products using the Sentinel 2 tiling grid as a
    reference.

    Current limitation is that vector features used must fit, or be completely contained
    inside a single Sentinel 2 tiling grid.

    For larger features, a mosaic of products will be necessary.

    This class was conceived first and foremost to be used for numerous smaller vector
    features, like polygon grids created from
    `geospatial_tools.vector.create_vector_grid`
    """

    def __init__(
        self,
        sentinel2_tiling_grid: GeoDataFrame,
        sentinel2_tiling_grid_column: str,
        vector_features: GeoDataFrame,
        vector_features_column: str,
        date_ranges: list[str] | None = None,
        max_cloud_cover: int = 5,
        max_no_data_value: int = 5,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """

        Args:
            sentinel2_tiling_grid: GeoDataFrame containing Sentinel 2 tiling grid
            sentinel2_tiling_grid_column: Name of the column in `sentinel2_tiling_grid` that contains the tile names
                (ex tile name: 10SDJ)
            vector_features: GeoDataFrame containing the vector features for which the best Sentinel 2
                products will be chosen for.
            vector_features_column: Name of the column in `vector_features` where the best Sentinel 2 products
                will be written to
            date_ranges: Date range used to search for Sentinel 2 products. should be created using
                `geospatial_tools.utils.create_date_range_for_specific_period` separately,
                or `BestProductsForFeatures.create_date_range` after initialization.
            max_cloud_cover: Maximum cloud cover used to search for Sentinel 2 products.
            logger: Logger instance
        """
        self.logger = logger
        self.sentinel2_tiling_grid = sentinel2_tiling_grid
        self.sentinel2_tiling_grid_column = sentinel2_tiling_grid_column
        self.sentinel2_tile_list = sentinel2_tiling_grid["name"].to_list()
        self.vector_features = vector_features
        self.vector_features_column = vector_features_column
        self.vector_features_best_product_column = "best_s2_product_id"
        self.vector_features_with_products = None
        self._date_ranges = date_ranges
        self._max_cloud_cover = max_cloud_cover
        self.max_no_data_value = max_no_data_value
        self.successful_results = {}
        self.incomplete_results = []
        self.error_results = []

    @property
    def max_cloud_cover(self):
        """Max % of cloud cover used for Sentinel 2 product search."""
        return self._max_cloud_cover

    @max_cloud_cover.setter
    def max_cloud_cover(self, max_cloud_cover: int) -> None:
        """

        Args:
          max_cloud_cover: int: Max percentage of cloud cover used for Sentinel 2 product search

        Returns:


        """
        self._max_cloud_cover = max_cloud_cover

    @property
    def date_ranges(self):
        """Date range used to search for Sentinel 2 products."""
        return self._date_ranges

    @date_ranges.setter
    def date_ranges(self, date_range: list[str]) -> None:
        """

        Args:
          date_range: list[str]:

        Returns:


        """
        self._date_ranges = date_range

    def create_date_ranges(self, start_year: int, end_year: int, start_month: int, end_month: int) -> list[str]:
        """
        This function create a list of date ranges.

        For example, I want to create date ranges for 2020 and 2021, but only for the months from March to May.
        I therefore expect to have 2 ranges: [2020-03-01 to 2020-05-30, 2021-03-01 to 2021-05-30].

        Handles the automatic definition of the last day for the end month, as well as periods that cross over years

        For example, I want to create date ranges for 2020 and 2022, but only for the months from November to January.
        I therefore expect to have 2 ranges: [2020-11-01 to 2021-01-31, 2021-11-01 to 2022-01-31].

        Args:
          start_year: Start year for ranges
          end_year: End year for ranges
          start_month: Starting month for each period
          end_month: End month for each period (inclusively)

        Returns:
            List of date ranges
        """
        self.date_ranges = create_date_range_for_specific_period(
            start_year=start_year, end_year=end_year, start_month_range=start_month, end_month_range=end_month
        )
        return self.date_ranges

    def find_best_complete_products(self, max_cloud_cover: int | None = None, max_no_data_value: int = 5) -> dict:
        """
        Finds the best complete products for each Sentinel 2 tiles. This function will filter out all products that have
        more than 5% of nodata values.

        Filtered out tiles will be stored in `self.incomplete` and tiles for which
        the search has found no results will be stored in `self.error_list`

        Args:
          max_cloud_cover: Max percentage of cloud cover allowed used for the search  (Default value = None)
          max_no_data_value: Max percentage of no-data coverage by individual Sentinel 2 product  (Default value = 5)

        Returns:
            Dictionary of product IDs and their corresponding Sentinel 2 tile names.
        """
        cloud_cover = self.max_cloud_cover
        if max_cloud_cover:
            cloud_cover = max_cloud_cover
        no_data_value = self.max_no_data_value
        if max_no_data_value:
            no_data_value = max_no_data_value

        tile_dict, incomplete_list, error_list = find_best_product_per_s2_tile(
            date_ranges=self.date_ranges,
            max_cloud_cover=cloud_cover,
            s2_tile_grid_list=self.sentinel2_tile_list,
            num_of_workers=4,
            max_no_data_value=no_data_value,
        )
        self.successful_results = tile_dict
        self.incomplete_results = incomplete_list
        if incomplete_list:
            self.logger.warning(
                "Warning, some of the input Sentinel 2 tiles do not have products covering the entire tile. "
                "These tiles will need to be handled differently (ex. creating a mosaic with multiple products"
            )
            self.logger.warning(f"Incomplete list: {incomplete_list}")
        self.error_results = error_list
        if error_list:
            self.logger.warning(
                "Warning, products for some Sentinel 2 tiles could not be found. "
                "Consider either extending date range input or max cloud cover"
            )
            self.logger.warning(f"Error list: {error_list}")
        return self.successful_results

    def select_best_products_per_feature(self) -> GeoDataFrame:
        """Return a GeoDataFrame containing the best products for each Sentinel 2 tile."""
        spatial_join_results = spatial_join_within(
            polygon_features=self.sentinel2_tiling_grid,
            polygon_column=self.sentinel2_tiling_grid_column,
            vector_features=self.vector_features,
            vector_column_name=self.vector_features_column,
        )
        write_best_product_ids_to_dataframe(
            spatial_join_results=spatial_join_results,
            tile_dictionary=self.successful_results,
            best_product_column=self.vector_features_best_product_column,
            s2_tiles_column=self.vector_features_column,
        )
        self.vector_features_with_products = spatial_join_results
        return self.vector_features_with_products

    def to_file(self, output_dir: str | pathlib.Path) -> None:
        """

        Args:
          output_dir: Output directory used to write to file
        """
        write_results_to_file(
            cloud_cover=self.max_cloud_cover,
            successful_results=self.successful_results,
            incomplete_results=self.incomplete_results,
            error_results=self.error_results,
            output_dir=output_dir,
        )


def sentinel_2_complete_tile_search(
    tile_id: int,
    date_ranges: list[str],
    max_cloud_cover: int,
    max_no_data_value: int = 5,
) -> tuple[int, str, float | None, float | None] | None:
    """

    Args:
      tile_id:
      date_ranges:
      max_cloud_cover:
      max_no_data_value: (Default value = 5)

    Returns:


    """
    client = StacSearch(PLANETARY_COMPUTER)
    collection = "sentinel-2-l2a"
    tile_ids = [tile_id]
    query = {"eo:cloud_cover": {"lt": max_cloud_cover}, "s2:mgrs_tile": {"in": tile_ids}}
    sortby = [{"field": "properties.eo:cloud_cover", "direction": "asc"}]

    client.search_for_date_ranges(
        date_ranges=date_ranges, collections=collection, query=query, sortby=sortby, limit=100
    )
    try:
        sorted_items = client.sort_results_by_cloud_coverage()
        if not sorted_items:
            return tile_id, "error: No results found", None, None
        filtered_items = client.filter_no_data(
            property_name="s2:nodata_pixel_percentage", max_no_data_value=max_no_data_value
        )
        if not filtered_items:
            return tile_id, "incomplete: No results found that cover the entire tile", None, None
        optimal_result = filtered_items[0]
        if optimal_result:
            return (
                tile_id,
                optimal_result.id,
                optimal_result.properties["eo:cloud_cover"],
                optimal_result.properties["s2:nodata_pixel_percentage"],
            )

    except (IndexError, TypeError) as error:
        print(error)
        return tile_id, f"error: {error}", None, None


def find_best_product_per_s2_tile(
    date_ranges: list[str],
    max_cloud_cover: int,
    s2_tile_grid_list: list,
    max_no_data_value: int = 5,
    num_of_workers: int = 4,
):
    """

    Args:
      date_ranges:
      max_cloud_cover:
      s2_tile_grid_list:
      max_no_data_value:  (Default value = 5)
      num_of_workers: (Default value = 4)

    Returns:


    """
    successful_results = {}
    for tile in s2_tile_grid_list:
        successful_results[tile] = ""
    incomplete_results = []
    error_results = []
    with ThreadPoolExecutor(max_workers=num_of_workers) as executor:
        future_to_tile = {
            executor.submit(
                sentinel_2_complete_tile_search,
                tile_id=tile,
                date_ranges=date_ranges,
                max_cloud_cover=max_cloud_cover,
                max_no_data_value=max_no_data_value,
            ): tile
            for tile in s2_tile_grid_list
        }

        for future in as_completed(future_to_tile):
            tile_id, optimal_result_id, max_cloud_cover, no_data = future.result()
            if optimal_result_id.startswith("error:"):
                error_results.append(tile_id)
                continue
            if optimal_result_id.startswith("incomplete:"):
                incomplete_results.append(tile_id)
                continue
            successful_results[tile_id] = {"id": optimal_result_id, "cloud_cover": max_cloud_cover, "no_data": no_data}
        cleaned_successful_results = {k: v for k, v in successful_results.items() if v != ""}
    return cleaned_successful_results, incomplete_results, error_results


def _get_best_product_id_for_each_grid_tile(
    s2_tile_search_results: dict, feature_s2_tiles: GeoDataFrame, logger: logging.Logger = LOGGER
) -> str | None:
    """

    Args:
      s2_tile_search_results:
      feature_s2_tiles:
      logger: (Default value = LOGGER)

    Returns:
        String value of product id
    """
    search_result_keys = s2_tile_search_results.keys()
    all_keys_present = all(item in search_result_keys for item in feature_s2_tiles)
    if not all_keys_present:
        logger.debug(
            f"Missmatch between search results and required tiles: [{feature_s2_tiles}] "
            f"not all found in [{search_result_keys}]"
            f"\n\tOnly partial results are available; skipping"
        )
        return None

    try:
        if len(feature_s2_tiles) == 1:
            s2_product_id = s2_tile_search_results[feature_s2_tiles[0]]["id"]
            return s2_product_id
        relevant_results = {k: s2_tile_search_results[k] for k in feature_s2_tiles if k in s2_tile_search_results}
        best_s2_tile = min(relevant_results, key=lambda k: relevant_results[k]["cloud_cover"])
        s2_product_id = relevant_results[best_s2_tile]["id"]
        return s2_product_id
    except KeyError as error:
        logger.warning(error)
        logger.warning("No products found")
        return None


def write_best_product_ids_to_dataframe(
    spatial_join_results: GeoDataFrame,
    tile_dictionary: dict,
    best_product_column: str = "best_s2_product_id",
    s2_tiles_column: str = "s2_tiles",
    logger: logging.Logger = LOGGER,
) -> None:
    """

    Args:
      spatial_join_results:
      tile_dictionary:
      best_product_column:
      s2_tiles_column:
      logger:

    Returns:


    """
    logger.info("Writing best product IDs to dataframe")
    spatial_join_results[best_product_column] = spatial_join_results[s2_tiles_column].apply(
        lambda x: _get_best_product_id_for_each_grid_tile(s2_tile_search_results=tile_dictionary, feature_s2_tiles=x)
    )


def write_results_to_file(
    cloud_cover: int,
    successful_results: dict,
    incomplete_results: list | None = None,
    error_results: list | None = None,
    output_dir: str | pathlib.Path = DATA_DIR,
    logger: logging.Logger = LOGGER,
) -> dict:
    """

    Args:
      cloud_cover:
      successful_results:
      incomplete_results:
      error_results:
      output_dir:
      logger:

    Returns:


    """
    tile_filename = output_dir / f"data_lt{cloud_cover}cc.json"
    with open(tile_filename, "w", encoding="utf-8") as json_file:
        json.dump(successful_results, json_file, indent=4)
    logger.info(f"Results have been written to {tile_filename}")

    incomplete_filename = "None"
    if incomplete_results:
        incomplete_dict = {"incomplete": incomplete_results}
        incomplete_filename = output_dir / f"incomplete_lt{cloud_cover}cc.json"
        with open(incomplete_filename, "w", encoding="utf-8") as json_file:
            json.dump(incomplete_dict, json_file, indent=4)
        logger.info(f"Incomplete results have been written to {incomplete_filename}")

    error_filename = "None"
    if error_results:
        error_dict = {"errors": error_results}
        error_filename = output_dir / f"errors_lt{cloud_cover}cc.json"
        with open(error_filename, "w", encoding="utf-8") as json_file:
            json.dump(error_dict, json_file, indent=4)
        logger.info(f"Errors results have been written to {error_filename}")

    return {
        "tile_filename": tile_filename,
        "incomplete_filename": incomplete_filename,
        "errors_filename": error_filename,
    }


def download_and_process_sentinel2_asset(
    product_id: str,
    product_bands: list[str],
    collections: str = "sentinel-2-l2a",
    target_projection: int | str | None = None,
    base_directory: str | pathlib.Path = DATA_DIR,
    delete_intermediate_files: bool = False,
    logger: logging.Logger = LOGGER,
) -> Asset:
    """
    This function downloads a Sentinel 2 product based on the product ID provided.

    It will download the individual asset bands provided in the `bands` argument,
    merge then all in a single tif and then reproject them to the input CRS.

    Args:
      product_id: ID of the Sentinel 2 product to be downloaded
      product_bands: List of the product bands to be downloaded
      collections: Collections to be downloaded from. Defaults to `sentinel-2-l2a`
      target_projection: The CRS project for the end product. If `None`, the reprojection step will be
        skipped
      stac_client: StacSearch client to used. A new one will be created if not provided
      base_directory: The base directory path where the downloaded files will be stored
      delete_intermediate_files: Flag to determine if intermediate files should be deleted. Defaults to False
      logger: Logger instance

    Returns:
        Asset instance
    """
    base_file_name = f"{base_directory}/{product_id}"
    merged_file = f"{base_file_name}_merged.tif"
    reprojected_file = f"{base_file_name}_reprojected.tif"

    merged_file_exists = pathlib.Path(merged_file).exists()
    reprojected_file_exists = pathlib.Path(reprojected_file).exists()

    if reprojected_file_exists:
        logger.info(f"Reprojected file [{reprojected_file}] already exists")
        asset = Asset(asset_id=product_id, bands=product_bands, reprojected_asset=reprojected_file)
        return asset

    if merged_file_exists:
        logger.info(f"Merged file [{merged_file}] already exists")
        asset = Asset(asset_id=product_id, bands=product_bands, merged_asset_path=merged_file)
        if target_projection:
            logger.info(f"Reprojecting merged file [{merged_file}]")
            asset.reproject_merged_asset(
                base_directory=base_directory,
                target_projection=target_projection,
                delete_merged_asset=delete_intermediate_files,
            )
        return asset

    stac_client = StacSearch(catalog_name=PLANETARY_COMPUTER)
    items = stac_client.search(collections=collections, ids=[product_id])
    logger.info(items)
    asset_list = stac_client.download_search_results(bands=product_bands, base_directory=base_directory)
    logger.info(asset_list)
    asset = asset_list[0]
    asset.merge_asset(base_directory=base_directory, delete_sub_items=delete_intermediate_files)
    if not target_projection:
        logger.info("Skipping reprojection")
        return asset
    if target_projection:
        asset.reproject_merged_asset(
            target_projection=target_projection,
            base_directory=base_directory,
            delete_merged_asset=delete_intermediate_files,
        )
    return asset
