from typing import Union

import geopandas as gpd
import numpy as np
from shapely import Polygon

from geospatial_tools.utils import create_logger

LOGGER = create_logger(__name__)


def create_vector_grid(
    bounding_box: Union[list, tuple], grid_size: float, logger=LOGGER, crs: str = None
) -> gpd.GeoDataFrame:
    """
    This function create a square grid polygon based on input bounds and grid size.

    :param bounding_box: Bounding box coordinates as (min_x, min_y, max_x, max_y)
    :param grid_size: Size of each grid cell. Unit is according to the projection of bounding box.
    :param crs: CRS of the grid cell
    :return:
    """

    min_x, min_y, max_x, max_y = bounding_box
    x_coords = np.arange(min_x, max_x, grid_size)
    y_coords = np.arange(min_y, max_y, grid_size)
    polygons = []
    for x in x_coords:
        for y in y_coords:
            polygons.append(Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)]))

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = gpd.GeoDataFrame(**properties)
    return grid


def create_grid_optimized(
    bounding_box: Union[list, tuple], grid_size: float, logger=LOGGER, crs: str = None
) -> gpd.GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size in EPSG:4326.
    This function uses NumPy for optimized performance.

    Parameters:
    bounding_box (tuple): The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size (float): The size of each grid cell in degrees.

    Returns:
    GeoDataFrame: A GeoDataFrame containing the grid polygons in EPSG:4326.
    """
    min_lon, min_lat, max_lon, max_lat = bounding_box
    lon_coords = np.arange(min_lon, max_lon, grid_size)
    lat_coords = np.arange(min_lat, max_lat, grid_size)

    # Generate grid coordinates
    lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)
    lon_grid = lon_grid.flatten()
    lat_grid = lat_grid.flatten()

    # Preallocate polygons array
    num_cells = len(lon_grid)
    polygons = np.empty(num_cells, dtype=object)

    # Create polygons using vectorized operations
    for i in range(num_cells):
        x, y = lon_grid[i], lat_grid[i]
        polygons[i] = Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)])

    # Create GeoDataFrame
    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = gpd.GeoDataFrame(**properties)
    return grid
