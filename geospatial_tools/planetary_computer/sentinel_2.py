import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from geospatial_tools import DATA_DIR
from geospatial_tools.stac import PLANETARY_COMPUTER, StacSearch


def sentinel_2_tile_search(tile_id, date_ranges, max_cloud_cover):
    search_client = StacSearch(PLANETARY_COMPUTER)
    collection = "sentinel-2-l2a"
    tile_ids = [tile_id]
    query = {"eo:cloud_cover": {"lt": max_cloud_cover}, "s2:mgrs_tile": {"in": tile_ids}}
    sortby = [{"field": "properties.eo:cloud_cover", "direction": "asc"}]

    search_client.stac_api_search_for_date_ranges(
        date_ranges=date_ranges, collections=collection, query=query, sortby=sortby, limit=100
    )
    try:
        sorted_items = search_client.sort_results_by_cloud_coverage()
        optimal_result = sorted_items[0]
        return tile_id, optimal_result.id, optimal_result.properties["eo:cloud_cover"]
    except (IndexError, TypeError) as error:
        print(error)
        return tile_id, f"error: {error}", None


def find_best_image_per_s2_tile(date_ranges, cloud_cover, s2_tile_grid_list, number_of_workers=4):
    tile_dict = {}
    for tile in s2_tile_grid_list:
        tile_dict[tile] = ""
    error_list = []
    with ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        future_to_tile = {
            executor.submit(sentinel_2_tile_search, tile, date_ranges, cloud_cover): tile for tile in s2_tile_grid_list
        }

        for future in as_completed(future_to_tile):
            tile_id, optimal_result_id, cloud_cover = future.result()
            tile_dict[tile_id] = {"id": optimal_result_id, "cloud_cover": cloud_cover}
            if optimal_result_id.startswith("error:"):
                error_list.append(tile_id)
    return tile_dict, error_list


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
