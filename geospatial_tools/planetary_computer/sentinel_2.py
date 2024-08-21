import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from geospatial_tools import DATA_DIR
from geospatial_tools.stac import PLANETARY_COMPUTER, StacSearch
from geospatial_tools.utils import create_date_range_for_specific_period, create_logger
from geospatial_tools.vector import spatial_join_within

LOGGER = create_logger(__name__)


class BestProductsForFeatures:
    def __init__(
        self,
        sentinel2_tiling_grid,
        sentinel2_tiling_grid_column,
        vector_features,
        vector_features_column,
        date_range=None,
        max_cloud_cover=None,
        logger: logging.Logger = LOGGER,
    ):
        self.logger = logger
        self.sentinel2_tiling_grid = sentinel2_tiling_grid
        self.sentinel2_tiling_grid_column = sentinel2_tiling_grid_column
        self.sentinel2_tile_list = sentinel2_tiling_grid["name"].to_list()
        self.vector_features = vector_features
        self.vector_features_column = vector_features_column
        self.vector_features_best_product_column = "best_s2_product_id"
        self.vector_features_with_products = None
        self.search_client = StacSearch(PLANETARY_COMPUTER)
        self._date_range = date_range
        self._max_cloud_cover = max_cloud_cover
        self.tile_dict = {}
        self.error_list = {}

    @property
    def max_cloud_cover(self):
        return self._max_cloud_cover

    @max_cloud_cover.setter
    def max_cloud_cover(self, max_cloud_cover):
        self._max_cloud_cover = max_cloud_cover

    @property
    def date_range(self):
        return self._date_range

    @date_range.setter
    def date_range(self, date_range):
        self._date_range = date_range

    def create_date_range(self, start_year, end_year, start_month, end_month):
        self.date_range = create_date_range_for_specific_period(
            start_year=start_year, end_year=end_year, start_month_range=start_month, end_month_range=end_month
        )

    def find_best_products(self):
        tile_dict, error_list = find_best_product_per_s2_tile(
            date_ranges=self.date_range,
            max_cloud_cover=self.max_cloud_cover,
            s2_tile_grid_list=self.sentinel2_tile_list,
            num_of_workers=4,
            search_client=self.search_client,
        )
        self.tile_dict = tile_dict
        self.error_list = error_list
        if error_list:
            self.logger.warning(
                "Warning, products for some Sentinel 2 tiles could not be found. "
                "Consider either extending date range input or max cloud cover"
            )
            self.logger.warning(f"Error list: {error_list}")
        return self.tile_dict

    def select_best_products_per_feature(self):
        spatial_join_results = spatial_join_within(
            polygon_features=self.sentinel2_tiling_grid,
            polygon_column=self.sentinel2_tiling_grid_column,
            vector_features=self.vector_features,
            vector_column_name=self.vector_features_column,
        )
        write_best_product_ids_to_dataframe(
            spatial_join_results=spatial_join_results,
            tile_dictionary=self.tile_dict,
            best_product_column=self.vector_features_best_product_column,
            s2_tiles_column=self.vector_features_column,
        )
        self.vector_features_with_products = spatial_join_results
        return self.vector_features_with_products


def sentinel_2_tile_search(tile_id, date_ranges, max_cloud_cover, search_client=None):
    client = search_client
    if client is None:
        client = StacSearch(PLANETARY_COMPUTER)
    collection = "sentinel-2-l2a"
    tile_ids = [tile_id]
    query = {"eo:cloud_cover": {"lt": max_cloud_cover}, "s2:mgrs_tile": {"in": tile_ids}}
    sortby = [{"field": "properties.eo:cloud_cover", "direction": "asc"}]

    client.stac_api_search_for_date_ranges(
        date_ranges=date_ranges, collections=collection, query=query, sortby=sortby, limit=100
    )
    try:
        sorted_items = client.sort_results_by_cloud_coverage()
        optimal_result = sorted_items[0]
        return tile_id, optimal_result.id, optimal_result.properties["eo:cloud_cover"]
    except (IndexError, TypeError) as error:
        print(error)
        return tile_id, f"error: {error}", None


def find_best_product_per_s2_tile(
    date_ranges, max_cloud_cover, s2_tile_grid_list, num_of_workers=4, search_client=None
):
    tile_dict = {}
    for tile in s2_tile_grid_list:
        tile_dict[tile] = ""
    error_list = []
    with ThreadPoolExecutor(max_workers=num_of_workers) as executor:
        future_to_tile = {
            executor.submit(
                sentinel_2_tile_search,
                tile_id=tile,
                date_ranges=date_ranges,
                max_cloud_cover=max_cloud_cover,
                search_client=search_client,
            ): tile
            for tile in s2_tile_grid_list
        }

        for future in as_completed(future_to_tile):
            tile_id, optimal_result_id, max_cloud_cover = future.result()
            tile_dict[tile_id] = {"id": optimal_result_id, "cloud_cover": max_cloud_cover}
            if optimal_result_id.startswith("error:"):
                error_list.append(tile_id)
    return tile_dict, error_list


def _get_best_product_id_for_each_grid_tile(s2_tile_search_results, feature_s2_tiles):
    print(f"s2_tiles_search_results: {s2_tile_search_results}")
    print(f"feature_s2_tiles: {feature_s2_tiles}")
    if len(feature_s2_tiles) == 1:
        s2_product_id = s2_tile_search_results[feature_s2_tiles[0]]["id"]
        return s2_product_id

    relevant_results = {k: s2_tile_search_results[k] for k in feature_s2_tiles if k in s2_tile_search_results}
    print(f"relevant_results: {relevant_results}")
    best_s2_tile = min(relevant_results, key=lambda k: relevant_results[k]["cloud_cover"])
    print(f"best_s2_tile: {best_s2_tile}")
    s2_product_id = relevant_results[best_s2_tile]["id"]
    print(f"s2_product_id: {s2_product_id}")
    return s2_product_id


def write_best_product_ids_to_dataframe(
    spatial_join_results, tile_dictionary, best_product_column="best_s2_product_id", s2_tiles_column="s2_tiles"
):
    spatial_join_results[best_product_column] = spatial_join_results[s2_tiles_column].apply(
        lambda x: _get_best_product_id_for_each_grid_tile(s2_tile_search_results=tile_dictionary, feature_s2_tiles=x)
    )


def write_results_to_file(cloud_cover, tile_dictionary, error_list=None):
    tile_filename = DATA_DIR / f"data_lt{cloud_cover}cc.json"
    with open(tile_filename, "w", encoding="utf-8") as json_file:
        json.dump(tile_dictionary, json_file, indent=4)
    print(f"Results have been written to {tile_filename}")

    error_filename = "None"
    if error_list:
        print(error_list)
        error_dict = {"errors": error_list}
        error_filename = DATA_DIR / f"errors_lt{cloud_cover}cc.json"
        with open(error_filename, "w", encoding="utf-8") as json_file:
            json.dump(error_dict, json_file, indent=4)
        print(f"Errors have been written to {error_filename}")

    return {"tile_filename": tile_filename, "errors_filename": error_filename}
