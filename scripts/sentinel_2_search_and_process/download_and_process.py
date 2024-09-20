import os
import pathlib

import geopandas as gpd
import typer
from geopandas import GeoDataFrame

from geospatial_tools import DATA_DIR
from geospatial_tools.planetary_computer.sentinel_2 import (
    download_and_process_sentinel2_asset,
)
from geospatial_tools.raster import clip_raster_with_polygon
from geospatial_tools.stac import Asset
from geospatial_tools.utils import create_logger

# Base directory
S2_SCRIPT_DIR = DATA_DIR / "sentinel_2_search_and_process"
PRODUCT_DIR = S2_SCRIPT_DIR / "products"

# Base files
BEST_PRODUCTS_FILE = S2_SCRIPT_DIR / "vector_tiles_800m_with_s2tiles.gpkg"

# Projection for final layers
CRS_PROJECTION = 5070

LOGGER = create_logger(__name__)


def _handle_product_list(product_list: str) -> list:
    parsed_product_list = []
    if product_list.endswith(".txt") and pathlib.Path(product_list).exists():
        with open(product_list, "r", encoding="utf-8") as f:
            for line in f:
                parsed_product_list.append(line.strip())
    if not product_list.endswith(".txt"):
        p_list_split = product_list.split(",")
        for p in p_list_split:
            if p:
                parsed_product_list.append(p.strip())
    return parsed_product_list


def _clip_raster(
    best_results: GeoDataFrame, group_by_product: GeoDataFrame, product_asset_list: list[Asset], num_of_workers: int = 4
) -> list[pathlib.Path]:
    clipped_raster_tiles = []
    for product in product_asset_list:
        s2_product_id = product.asset_id
        product_path = product.reprojected_asset_path
        product_id_series = group_by_product[group_by_product["best_s2_product_id"] == s2_product_id]
        # Since it's grouped by product id, there should always be only one row in the series
        feature_ids = product_id_series["feature_id"].iloc[0]
        vector_features = best_results[best_results["feature_id"].isin(feature_ids)]

        clipped_tiles = clip_raster_with_polygon(
            raster_image=product_path,
            polygon_layer=vector_features,
            base_output_filename=s2_product_id,
            output_dir=PRODUCT_DIR / "sentinel2_clips",
            num_of_workers=num_of_workers,
        )
        clipped_raster_tiles.extend(clipped_tiles)
    return clipped_raster_tiles


def download_and_process(
    product_list: str,
    download_dir: str = PRODUCT_DIR,
    best_products_file: str = BEST_PRODUCTS_FILE,
    target_crs: int = CRS_PROJECTION,
    num_of_workers: int = 4,
    delete_products: bool = False,
    delete_tiles: bool = False,
    debug: bool = False,
):
    """
    This command will download and process all products given in the product list.

    The `product_list` argument can
    either be a path to a text file containing a list of product ids (one id per line, no commas, as generated per
    the `product_search.py` script, or a comma separated list of product ids, ex
    `S2A_MSIL2A_20200603T184921_R113_T10SEF_20200826T000100,S2A_MSIL2A_20200609T154911_R054_T18TVL_20200826T173834`
    """
    if debug:
        os.environ["GEO_LOG_LEVEL"] = "DEBUG"
    parsed_product_list = _handle_product_list(product_list)
    LOGGER.info(f"Will download and process the following products: {parsed_product_list}")
    if not parsed_product_list:
        LOGGER.error("Error - Product list not found!")
        return None

    LOGGER.info(f"Loading best results file {best_products_file}")
    best_results = gpd.read_file(best_products_file)

    LOGGER.info("Grouping results by product")
    group_by_product = best_results.groupby("best_s2_product_id")["feature_id"].agg(list).reset_index()

    bands = ["B02", "B03", "B04", "B08", "visual"]
    product_asset_list = [
        download_and_process_sentinel2_asset(
            product_id=p,
            product_bands=bands,
            base_directory=download_dir,
            target_projection=target_crs,
            delete_intermediate_files=True,
        )
        for p in parsed_product_list
    ]

    LOGGER.info("Starting clipping process")
    clipped_raster_tiles = _clip_raster(
        best_results=best_results,
        group_by_product=group_by_product,
        product_asset_list=product_asset_list,
        num_of_workers=num_of_workers,
    )

    #
    # Do something with the tiles
    #
    # Ex.
    # for tile in clipped_raster_tiles:
    #     do something ...

    #
    # Cleanup tiles and downloaded products
    #
    if delete_products:
        for product in product_asset_list:
            product.delete_reprojected_asset()

    if delete_tiles:
        for tile in clipped_raster_tiles:
            tile.unlink(missing_ok=True)


if __name__ == "__main__":
    typer.run(download_and_process)
