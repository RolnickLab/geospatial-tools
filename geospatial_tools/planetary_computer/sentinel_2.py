import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from geopandas import GeoDataFrame

from geospatial_tools import DATA_DIR
from geospatial_tools.stac import PLANETARY_COMPUTER, StacSearch
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
        date_ranges: list[str] = None,
        max_cloud_cover: int = None,
        logger: logging.Logger = LOGGER,
    ):
        """

        Parameters
        ----------
        sentinel2_tiling_grid
            GeoDataFrame containing Sentinel 2 tiling grid
        sentinel2_tiling_grid_column
            Name of the column in `sentinel2_tiling_grid` that contains the tile names
            (ex tile name: 10SDJ)
        vector_features
            GeoDataFrame containing the vector features for which the best Sentinel 2
            products will be chosen for.
        vector_features_column
            Name of the column in `vector_features` where the best Sentinel 2 products
            will be written to
        date_ranges
            Date range used to search for Sentinel 2 products. should be created using
            `geospatial_tools.utils.create_date_range_for_specific_period` separately,
            or `BestProductsForFeatures.create_date_range` after initialization.
        max_cloud_cover
            Maximum cloud cover used to search for Sentinel 2 products.
        logger
            Logger instance
        """
        self.logger = logger
        self.sentinel2_tiling_grid = sentinel2_tiling_grid
        self.sentinel2_tiling_grid_column = sentinel2_tiling_grid_column
        self.sentinel2_tile_list = sentinel2_tiling_grid["name"].to_list()
        self.vector_features = vector_features
        self.vector_features_column = vector_features_column
        self.vector_features_best_product_column = "best_s2_product_id"
        self.vector_features_with_products = None
        self.search_client = StacSearch(PLANETARY_COMPUTER)
        self._date_ranges = date_ranges
        self._max_cloud_cover = max_cloud_cover
        self.successful_results = {}
        self.incomplete_results = []
        self.error_results = []

    @property
    def max_cloud_cover(self):
        return self._max_cloud_cover

    @max_cloud_cover.setter
    def max_cloud_cover(self, max_cloud_cover: int):
        self._max_cloud_cover = max_cloud_cover

    @property
    def date_ranges(self):
        return self._date_ranges

    @date_ranges.setter
    def date_ranges(self, date_range: list[str]):
        self._date_ranges = date_range

    def create_date_ranges(self, start_year: int, end_year: int, start_month: int, end_month: int) -> list[str]:
        """
        This function create a list of date ranges.

        For example, I want to create date ranges for 2020 and 2021, but only for the months from March to May.
        I therefore expect to have 2 ranges: [2020-03-01 to 2020-05-30, 2021-03-01 to 2021-05-30].

        Handles the automatic definition of the last day for the end month, as well as periods that cross over years

        For example, I want to create date ranges for 2020 and 2022, but only for the months from November to January.
        I therefore expect to have 2 ranges: [2020-11-01 to 2021-01-31, 2021-11-01 to 2022-01-31].

        Parameters
        ----------
        start_year
            Start year for ranges
        end_year
            End year for ranges
        start_month
            Starting month for each period
        end_month
            End month for each period (inclusively)

        Returns
        -------
            List containing datetime date ranges
        """
        self.date_ranges = create_date_range_for_specific_period(
            start_year=start_year, end_year=end_year, start_month_range=start_month, end_month_range=end_month
        )
        return self.date_ranges

    def find_best_complete_products(self) -> dict:
        """
        Finds the best complete products for each Sentinel 2 tiles. This function will filter out all products that have
        more than 5% of nodata values.

        Filtered out tiles will be stored in `self.incomplete` and tiles for which
        the search has found no results will be stored in `self.error_list`

        Returns
        -------
            tile_dict:
                Tile dictionary containing the successful search results.
        """
        tile_dict, incomplete_list, error_list = find_best_product_per_s2_tile(
            date_ranges=self.date_ranges,
            max_cloud_cover=self.max_cloud_cover,
            s2_tile_grid_list=self.sentinel2_tile_list,
            num_of_workers=4,
            search_client=self.search_client,
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
        """

        Returns
        -------

        """
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

    def to_file(self):
        write_results_to_file(
            cloud_cover=self.max_cloud_cover,
            successful_results=self.successful_results,
            incomplete_results=self.incomplete_results,
            error_results=self.error_results,
        )


def sentinel_2_complete_tile_search(
    tile_id: int,
    date_ranges: list[str],
    max_cloud_cover: int,
    max_no_data_value: int = 5,
    search_client: StacSearch = None,
) -> tuple[int, str, Optional[float]]:
    client = search_client
    if client is None:
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
            return tile_id, "error: No results found", None
        optimal_result = None
        for item in sorted_items:
            if item.properties["s2:nodata_pixel_percentage"] < max_no_data_value:
                optimal_result = item
                return tile_id, optimal_result.id, optimal_result.properties["eo:cloud_cover"]
        if not optimal_result:
            return tile_id, "incomplete: No results found that cover the entire tile", None

    except (IndexError, TypeError) as error:
        print(error)
        return tile_id, f"error: {error}", None


def find_best_product_per_s2_tile(
    date_ranges: list[str],
    max_cloud_cover: int,
    s2_tile_grid_list: list,
    num_of_workers: int = 4,
    search_client: StacSearch = None,
):
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
                search_client=search_client,
            ): tile
            for tile in s2_tile_grid_list
        }

        for future in as_completed(future_to_tile):
            tile_id, optimal_result_id, max_cloud_cover = future.result()
            if optimal_result_id.startswith("error:"):
                error_results.append(tile_id)
                continue
            if optimal_result_id.startswith("incomplete:"):
                incomplete_results.append(tile_id)
                continue
            successful_results[tile_id] = {"id": optimal_result_id, "cloud_cover": max_cloud_cover}
        cleaned_successful_results = {k: v for k, v in successful_results.items() if v != ""}
    return cleaned_successful_results, incomplete_results, error_results


def _get_best_product_id_for_each_grid_tile(
    s2_tile_search_results: dict, feature_s2_tiles: GeoDataFrame, logger: logging.Logger = LOGGER
) -> Optional[str]:
    search_result_keys = s2_tile_search_results.keys()
    all_keys_present = all(item in search_result_keys for item in feature_s2_tiles)
    if not all_keys_present:
        logger.warning(
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
):
    logger.info("Writing best product IDs to dataframe")
    spatial_join_results[best_product_column] = spatial_join_results[s2_tiles_column].apply(
        lambda x: _get_best_product_id_for_each_grid_tile(s2_tile_search_results=tile_dictionary, feature_s2_tiles=x)
    )


def write_results_to_file(
    cloud_cover: int, successful_results: dict, incomplete_results: list = None, error_results: list = None
) -> dict:
    tile_filename = DATA_DIR / f"data_lt{cloud_cover}cc.json"
    with open(tile_filename, "w", encoding="utf-8") as json_file:
        json.dump(successful_results, json_file, indent=4)
    print(f"Results have been written to {tile_filename}")

    incomplete_filename = "None"
    if incomplete_results:
        print(incomplete_results)
        incomplete_dict = {"incomplete": incomplete_results}
        incomplete_filename = DATA_DIR / f"incomplete_lt{cloud_cover}cc.json"
        with open(incomplete_filename, "w", encoding="utf-8") as json_file:
            json.dump(incomplete_dict, json_file, indent=4)
        print(f"Incomplete results have been written to {incomplete_filename}")

    error_filename = "None"
    if error_results:
        print(error_results)
        error_dict = {"errors": error_results}
        error_filename = DATA_DIR / f"errors_lt{cloud_cover}cc.json"
        with open(error_filename, "w", encoding="utf-8") as json_file:
            json.dump(error_dict, json_file, indent=4)
        print(f"Errors results have been written to {error_filename}")

    return {
        "tile_filename": tile_filename,
        "incomplete_filename": incomplete_filename,
        "errors_filename": error_filename,
    }
