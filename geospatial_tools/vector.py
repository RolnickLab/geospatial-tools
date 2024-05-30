import logging
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from typing import Union

import geopandas as gpd
import numpy as np
from shapely import Polygon

from geospatial_tools.utils import create_logger

LOGGER = create_logger(__name__)


def create_vector_grid(
    bounding_box: Union[list, tuple], grid_size: float, logger: logging.Logger = LOGGER, crs: str = None
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

    # Preallocate polygon array
    num_cells = len(lon_grid)
    polygons = np.empty(num_cells, dtype=object)

    for i in range(num_cells):
        x, y = lon_grid[i], lat_grid[i]
        polygons[i] = Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)])

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = gpd.GeoDataFrame(**properties)
    grid.sindex
    return grid


def create_grid_chunk(chunk):
    lon_coords, lat_coords, grid_size = chunk
    polygons = []
    for lon, lat in zip(lon_coords, lat_coords):
        polygons.append(
            Polygon([(lon, lat), (lon + grid_size, lat), (lon + grid_size, lat + grid_size), (lon, lat + grid_size)])
        )
    return polygons


def create_vector_grid_parallel(
    bounding_box: Union[list, tuple],
    grid_size: float,
    crs: str = None,
    num_processes: int = None,
    logger: logging.Logger = LOGGER,
) -> gpd.GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size in EPSG:4326.
    This function uses NumPy for optimized performance and ProcessPoolExecutor for parallel execution.

    Parameters:
    bounding_box (tuple): The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size (float): The size of each grid cell in degrees.
    crs (str): Coordinate reference system for the resulting GeoDataFrame.
    num_processes (int): The number of processes to use for parallel execution.
                         Defaults to the min of number of CPU cores or number of cells in the grid
    logger: Optional logger for logging.

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

    # Prepare chunked grid
    num_cells = len(lon_grid)
    workers = min(cpu_count(), num_cells)
    if num_processes:
        workers = num_processes
    chunk_size = (num_cells + workers - 1) // workers
    chunks = [
        (lon_grid[i : i + chunk_size], lat_grid[i : i + chunk_size], grid_size) for i in range(0, num_cells, chunk_size)
    ]

    polygons = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = executor.map(create_grid_chunk, chunks)
        for result in results:
            polygons.extend(result)

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = gpd.GeoDataFrame(**properties)
    grid.sindex
    return grid
