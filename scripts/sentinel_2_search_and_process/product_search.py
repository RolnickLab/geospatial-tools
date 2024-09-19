import os
import pathlib
import warnings

import geopandas as gpd
import typer
from pyogrio.errors import DataSourceError

from geospatial_tools import DATA_DIR
from geospatial_tools.planetary_computer.sentinel_2 import BestProductsForFeatures
from geospatial_tools.utils import create_logger
from geospatial_tools.vector import (
    create_vector_grid_parallel,
    dask_spatial_join,
    select_polygons_by_location,
    to_geopackage,
)

warnings.filterwarnings("ignore", category=FutureWarning)

LOGGER = create_logger(__name__)
###
# Base arguments
###

# Base directory
S2_SCRIPT_DIR = DATA_DIR / "sentinel_2_search_and_process"

# Base files
USA_POLYGON_FILE = DATA_DIR / "usa_polygon_5070.gpkg"
S2_USA_GRID_FILE = DATA_DIR / "s2_grid_usa_polygon_5070.gpkg"

# Grid size for vector polygons
GRID_SIZE = 800
# Projection for final layers
CRS_PROJECTION = 5070

# Name of column containing s2 tile ids
S2_FEATURE_NAME_COLUMN = "name"
# Name of column that will contain S2 tile ids that contain each vector polygon
VECTOR_COLUMN_NAME = "s2_tiles"

# Date range arguments. This will look for the months of June and July, from 2020 to 2024
START_YEAR = 2020
END_YEAR = 2024
START_MONTH = 6
END_MONTH = 7

# Max cloud cover to use as search parameter
MAX_CLOUD_COVER = 15

# Processing arguments
NUM_OF_WORKERS_VECTOR_GRID = 16
NUM_OF_WORKERS_SPATIAL_SELECT = 8

###
# Base data
###

# The USA polygon is base off 2018's `cb_2018_us_nation_5m` shapefile, taken from here:
# https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
#
# It was then processed using QGIS to keep only the contiguous states, without any islands.
#
# The Sentinel 2 grid was taken from the kml file found here:
# https://sentiwiki.copernicus.eu/web/s2-products

###
# Initial pre-processing
###

# The layers below were processed using QGIS.
#
# For the purpose of this analysis, only the contiguous lower 48 states have been
# conserved; smaller islands/land masses have also been striped.
#
# The S2 tiling grid has been trimmed to keep only the grid cells that overlap with the
# contiguous states.
#
# Since our area of study is quite large, the `EPSG:5070` projection was chosen, as it
# covers the whole area, introduces minimal distortion while preserving area.
#


def product_search(
    polygon_file: str = USA_POLYGON_FILE,
    sentinel2_grid_file: str = S2_USA_GRID_FILE,
    output_dir: str = str(S2_SCRIPT_DIR),
    grid_size: int = GRID_SIZE,
    target_crs: int = CRS_PROJECTION,
    max_cloud_cover: int = MAX_CLOUD_COVER,
    s2_feature_name: str = S2_FEATURE_NAME_COLUMN,
    vector_column_name: str = VECTOR_COLUMN_NAME,
    num_workers_vector_grid: int = NUM_OF_WORKERS_VECTOR_GRID,
    num_workers_spatial_select: int = NUM_OF_WORKERS_SPATIAL_SELECT,
    debug: bool = False,
):  # pylint: disable=R0914
    """
    This function searches for Sentinel 2 products.

    Takes 2 file paths as input;
    `polygon_file` and `sentinel2_grid_file`, for the main region of interest, and the
    Sentinel 2 griding tiles, respectively. Both these files need to be in the same
    projection, must be in a projected projection (i.e. in meters), and this projection
    must be the same as `crs`.
    """
    if debug:
        os.environ["GEO_LOG_LEVEL"] = "DEBUG"
    usa_polygon = gpd.read_file(polygon_file)
    s2_grid = gpd.read_file(sentinel2_grid_file)

    # Creating our grid
    #
    # From this, we want to create a grid of square polygons with which we will later on
    # query the [Planetary Computer](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a)
    # Sentinel 2 dataset and clip the selected Sentinel 2 images.
    output_dir = pathlib.Path(output_dir)

    grid_800m_filename = output_dir / "polygon_grid_800m.gpkg"
    bbox = usa_polygon.total_bounds
    try:
        LOGGER.info(f"Trying to load {grid_800m_filename}, if it exists")
        grid_800m = gpd.read_file(grid_800m_filename)
        LOGGER.info("Succeeded!")
    except DataSourceError:
        LOGGER.info(f"Failed to load {grid_800m_filename}")
        LOGGER.info("Starting processing for [create_vector_grid_parallel]")
        grid_800m = create_vector_grid_parallel(
            bounding_box=bbox, num_of_workers=num_workers_vector_grid, grid_size=grid_size, crs=target_crs
        )
        to_geopackage(grid_800m, grid_800m_filename)
        LOGGER.info(f"Printing len(grid_parallel) to check if grid contains same amount of polygons : {len(grid_800m)}")

    # Selecting the useful polygons
    #
    # Now, since our grid was created using the extent of our input polygon (continental USA),
    # we need to filter out the polygons that do not intersect with it.

    # Doing this in Python is not the most efficient way to do things, but since it's a
    # step that shouldn't be done over and over, it's not that critical.

    # If ever you need to do this step in an efficient way because the data is just too
    # big or too complex, it would be better off going through QGIS, PyGQIS, GDAL or
    # some other more efficient way to do this operation.

    usa_polygon_grid_800m_filename = output_dir / "usa_polygon_grid_800m.gpkg"
    try:
        LOGGER.info(f"Trying to load {usa_polygon_grid_800m_filename}, if it exists")
        usa_polygon_grid_800m = gpd.read_file(usa_polygon_grid_800m_filename)
        LOGGER.info("Succeeded!")
    except DataSourceError:
        LOGGER.info(f"Failed to load {usa_polygon_grid_800m_filename}")
        LOGGER.info("Starting intersect selection")
        usa_polygon_grid_800m = select_polygons_by_location(
            select_features_from=grid_800m,
            intersected_with=usa_polygon,
            num_of_workers=num_workers_spatial_select,
            join_function=dask_spatial_join,
        )
        to_geopackage(usa_polygon_grid_800m, usa_polygon_grid_800m_filename)

    # Finding the best image for each S2 tiling grid

    # Initiating our client
    # s2_tile_grid_list = s2_grid["name"].to_list()
    best_products_client = BestProductsForFeatures(
        sentinel2_tiling_grid=s2_grid,
        sentinel2_tiling_grid_column=s2_feature_name,
        vector_features=usa_polygon_grid_800m,
        vector_features_column=vector_column_name,
        max_cloud_cover=max_cloud_cover,
    )

    # Executing the search
    #
    # This search looks only for complete products, meaning products with less than
    # 5 percent of nodata.

    best_products_client.create_date_ranges(START_YEAR, END_YEAR, START_MONTH, END_MONTH)
    best_products_client.find_best_complete_products()
    best_products_client.to_file(output_dir=output_dir)

    # Selecting the best products for each vector tile
    #
    # This step is necessary as some of our vector polygons can be withing multiple S2 tiles.
    # The best available S2 tile is therefore selected for each vector polygon.

    best_results_path = output_dir / "vector_tiles_800m_with_s2tiles.gpkg"
    best_results = best_products_client.select_best_products_per_feature()

    # Writing the results to file
    to_geopackage(best_results, best_results_path)

    # Grouping vector tiles by product
    group_by_product_path = output_dir / "vector_tiles_800m_grouped_by_s2_product.gpkg"
    LOGGER.info(f"Grouping vector tiles by product and saving to dataframe : {group_by_product_path}")
    grouped_gdf = best_results.groupby("best_s2_product_id")["feature_id"].agg(list).reset_index()
    to_geopackage(gdf=grouped_gdf, filename=group_by_product_path)

    # Saving the product list
    product_list_path = output_dir / "product_list.txt"
    LOGGER.info(f"Saving product list to {product_list_path}")
    product_list = grouped_gdf["best_s2_product_id"].tolist()
    with open(product_list_path, "w", encoding="utf-8") as f:
        for item in product_list:
            f.write(f"{item}\n")


if __name__ == "__main__":
    typer.run(product_search)
