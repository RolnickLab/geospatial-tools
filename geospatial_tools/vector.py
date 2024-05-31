import logging
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path
from typing import Union

import geopandas as gpd
import numpy as np
from shapely import Polygon

from geospatial_tools.utils import GEOPACKAGE_DRIVER, create_logger

LOGGER = create_logger(__name__)


def get_coords(bounding_box: Union[list, tuple], grid_size: float) -> np.ndarray:
    """_summary_

    Parameters
    ----------
    bounding_box : Union[list, tuple]
        _description_
    grid_size : float
        _description_

    Returns
    -------
    _type_
        _description_
    """
    min_lon, min_lat, max_lon, max_lat = bounding_box
    lat_coords = np.arange(min_lat, max_lat, grid_size)
    lon_coords = np.arange(min_lon, max_lon, grid_size)
    return lat_coords, lon_coords


def generate_grid_coords(lat_coords: np.ndarray, lon_coords: np.ndarray):
    """_summary_

    Parameters
    ----------
    lat_coords : np.ndarray
        _description_
    lon_coords : np.ndarray
        _description_

    Returns
    -------
    _type_
        _description_
    """
    lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)
    lat_grid = lat_grid.flatten()
    lon_grid = lon_grid.flatten()
    return lat_grid, lon_grid


def create_vector_grid(
    bounding_box: Union[list, tuple], grid_size: float, logger: logging.Logger = LOGGER, crs: str = None
) -> gpd.GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size in EPSG:4326.
    This function uses NumPy for optimized performance.

    Parameters:
    -----------
    bounding_box (tuple):
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size (float):
        The size of each grid cell in degrees.

    Returns:
    --------
    GeoDataFrame: A GeoDataFrame containing the grid polygons in EPSG:4326.
    """
    lat_coords, lon_coords = get_coords(bounding_box, grid_size)
    lat_grid, lon_grid = generate_grid_coords(lat_coords, lon_coords)

    num_cells = len(lon_grid)
    logger.info(f"Allocationg polygon array for [{num_cells}] polygons")
    polygons = np.empty(num_cells, dtype=object)

    for i in range(num_cells):
        x, y = lon_grid[i], lat_grid[i]
        polygons[i] = Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)])

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = gpd.GeoDataFrame(**properties)
    grid.sindex  # pylint: disable=W0104
    return grid


def create_grid_chunk(chunk: gpd.GeoDataFrame):
    """_summary_

    Parameters
    ----------
    chunk : gpd.GeoDataFrame
        _description_

    Returns
    -------
    _type_
        _description_
    """
    lon_coords, lat_coords, grid_size = chunk
    polygons = []
    for lon, lat in zip(lon_coords, lat_coords):
        polygons.append(
            Polygon([(lon, lat), (lon + grid_size, lat), (lon + grid_size, lat + grid_size), (lon, lat + grid_size)])
        )
    return polygons


def generate_grid_chunks(grid_size: int, lat_grid: np.ndarray, lon_grid: np.ndarray, num_cells: int, workers: int):
    """_summary_

    Parameters
    ----------
    grid_size : int
        _description_
    lat_grid : np.ndarray
        _description_
    lon_grid : np.ndarray
        _description_
    num_cells : int
        _description_
    workers : int
        _description_

    Returns
    -------
    _type_
        _description_
    """
    chunk_size = (num_cells + workers - 1) // workers
    chunks = [
        (lon_grid[i : i + chunk_size], lat_grid[i : i + chunk_size], grid_size) for i in range(0, num_cells, chunk_size)
    ]

    return chunks


def create_vector_grid_parallel(
    bounding_box: Union[list, tuple],
    grid_size: float,
    crs: str = None,
    num_processes: int = None,
    logger: logging.Logger = LOGGER,
) -> gpd.GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size.
    This function uses NumPy for optimized performance and ProcessPoolExecutor for parallel execution.

    Parameters:
    -----------
    bounding_box : tuple
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size : float
        The size of each grid cell in degrees.
    crs : str
        Coordinate reference system for the resulting GeoDataFrame.
    num_processes : int
        The number of processes to use for parallel execution. Defaults to the min of number of CPU cores or number
        of cells in the grid
    logger : Optional logger for logging.

    Returns:
    --------
    GeoDataFrame: A GeoDataFrame containing the grid polygons.
    """
    lat_coords, lon_coords = get_coords(bounding_box, grid_size)
    lat_grid, lon_grid = generate_grid_coords(lat_coords, lon_coords)

    num_cells = len(lon_grid)
    workers = min(cpu_count(), num_cells)
    if num_processes:
        workers = num_processes
    logger.info(f"Number of workers : {workers}")

    chunks = generate_grid_chunks(grid_size, lat_grid, lon_grid, num_cells, workers)

    polygons = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = executor.map(create_grid_chunk, chunks)
        for result in results:
            polygons.extend(result)

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = gpd.GeoDataFrame(**properties)
    grid.sindex  # pylint: disable=W0104
    return grid


def to_geopackage(gdf: gpd.GeoDataFrame, filename: str):
    """
    Save GeoDataFrame to a Geopackage file.

    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to save.
    filename : str
        The filename to save to.

    Returns:
    --------
    None
    """
    filename_path = Path(filename)
    gdf.to_file(filename_path, driver=GEOPACKAGE_DRIVER, mode="w")


def to_geopackage_chunked(gdf: gpd.GeoDataFrame, filename: str, chunk_size: int = 500000):
    """
    Save GeoDataFrame to a Geopackage file.

    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to save.
    filename : str
        The filename to save to.
    chunk_size : int
        The number of rows per chunk.

    Returns:
    --------
    None
    """
    filename_path = Path(filename)
    if filename_path.exists():
        filename_path.unlink()

    chunk = gdf.iloc[0:chunk_size]
    chunk.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="w")

    for i in range(chunk_size, len(gdf), chunk_size):
        chunk = gdf.iloc[i : i + chunk_size]
        chunk.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="a")
