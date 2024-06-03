import logging
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path
from typing import Union

import numpy as np
from geopandas import GeoDataFrame
from numpy import ndarray
from shapely import Polygon

from geospatial_tools.utils import GEOPACKAGE_DRIVER, create_logger

LOGGER = create_logger(__name__)


def create_grid_coordinates(
    bounding_box: Union[list, tuple], grid_size: float, logger=LOGGER
) -> tuple[ndarray, ndarray]:
    """Create grid coordinates based on input bounding box and grid size.

    Parameters
    -----------
    bounding_box : Union[list, tuple]
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
        Unit needs to be based on projection used (meters, degrees, etc.).
    grid_size : float
        Cell size for grid. Unit needs to be based on projection used (meters, degrees, etc.).
    logger : logging.Logger
        Optional logger for logging.

    Returns
    --------
    tuple(ndarray, ndarray)
        Tuple containing the longitude and latitude grid coordinates.
    """
    logger.info(f"Creating grid coordinates for bounding box [{bounding_box}]")
    min_lon, min_lat, max_lon, max_lat = bounding_box
    lon_coords = np.arange(start=min_lon, stop=max_lon, step=grid_size)
    lat_coords = np.arange(start=min_lat, stop=max_lat, step=grid_size)
    return lon_coords, lat_coords


def generate_flattened_grid_coords(lon_coords: ndarray, lat_coords: ndarray, logger=LOGGER) -> tuple[ndarray, ndarray]:
    """Takes in previously created grid coordinates and flattens them.

    Parameters
    -----------
    lon_coords : ndarray
        Longitude grid coordinates
    lat_coords : ndarray
        Latitude grid coordinates
    logger : logging.Logger
        Optional logger for logging.

    Returns
    --------
     tuple[ndarray, ndarray]
        Flattened longitude and latitude grids.
    """

    logger.info("Creating flattened grid coordinates")
    lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)
    lon_grid = lon_grid.flatten()
    lat_grid = lat_grid.flatten()
    return lon_grid, lat_grid


def _create_polygons_from_coords_chunk(chunk: tuple[ndarray, ndarray, float]) -> list[Polygon]:
    """Helper function to create polygons from input coordinates chunk.

    Parameters
    -----------
    chunk : tuple[ndarray, ndarray, float]
        Coordinates chunk as a tuple (longitude coords, latitude coords, grid size).

    Returns
    --------
    list:
        List of polygons.
    """
    lon_coords, lat_coords, grid_size = chunk
    polygons = []
    for lon, lat in zip(lon_coords, lat_coords):
        polygons.append(
            Polygon([(lon, lat), (lon + grid_size, lat), (lon + grid_size, lat + grid_size), (lon, lat + grid_size)])
        )
    return polygons


def create_vector_grid(
    bounding_box: Union[list, tuple], grid_size: float, crs: str = None, logger: logging.Logger = LOGGER
) -> GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size.
    This function uses NumPy vectorized arrays for optimized performance.

    Parameters
    -----------
    bounding_box : Union[list, tuple]
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size : float
        The size of each grid cell in degrees.
    crs : str
        CRS code for projection. ex. 'EPSG:4326'
    logger : logging.Logger
        Optional logger for logging.

    Returns
    --------
    GeoDataFrame:
        GeoDataFrame containing the grid polygons.
    """
    lon_coords, lat_coords = create_grid_coordinates(bounding_box=bounding_box, grid_size=grid_size, logger=logger)
    lon_flat_grid, lat_flat_grid = generate_flattened_grid_coords(
        lat_coords=lat_coords, lon_coords=lon_coords, logger=logger
    )

    num_cells = len(lon_flat_grid)
    logger.info(f"Allocating polygon array for [{num_cells}] polygons")
    polygons = np.empty(num_cells, dtype=object)

    for i in range(num_cells):
        x, y = lon_flat_grid[i], lat_flat_grid[i]
        polygons[i] = Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)])

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid = GeoDataFrame(**properties)
    grid.sindex  # pylint: disable=W0104
    return grid


def create_vector_grid_parallel(
    bounding_box: Union[list, tuple],
    grid_size: float,
    crs: str = None,
    num_processes: int = None,
    logger: logging.Logger = LOGGER,
) -> GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size.
    This function uses NumPy for optimized performance and ProcessPoolExecutor for parallel execution.

    Parameters
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
    logger : logging.Logger
        Optional logger for logging.

    Returns
    --------
    GeoDataFrame:
        GeoDataFrame containing the grid polygons.
    """
    lon_coords, lat_coords = create_grid_coordinates(bounding_box=bounding_box, grid_size=grid_size, logger=logger)
    lon_flat_grid, lat_flat_grid = generate_flattened_grid_coords(
        lat_coords=lat_coords, lon_coords=lon_coords, logger=logger
    )

    num_cells = len(lon_flat_grid)
    workers = min(cpu_count(), num_cells)
    if num_processes:
        workers = num_processes

    logger.info(f"Number of workers used: {workers}")
    logger.info(f"Allocating polygon array for [{num_cells}] polygons")

    chunk_size = (num_cells + workers - 1) // workers
    chunks = [
        (lon_flat_grid[i : i + chunk_size], lat_flat_grid[i : i + chunk_size], grid_size)
        for i in range(0, num_cells, chunk_size)
    ]

    polygons = []
    logger.info("Creating polygons from chunk")
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = executor.map(_create_polygons_from_coords_chunk, chunks)
        for result in results:
            polygons.extend(result)

    properties = {"data": {"geometry": polygons}}
    if crs:
        properties["crs"] = crs
    grid: GeoDataFrame = GeoDataFrame(**properties)
    grid.sindex  # pylint: disable=W0104
    return grid


def to_geopackage(gdf: GeoDataFrame, filename: str) -> str:
    """
    Save GeoDataFrame to a Geopackage file.

    Parameters
    -----------
    gdf : GeoDataFrame
        The GeoDataFrame to save.
    filename : str
        The filename to save to.

    Returns
    --------
    str:
        file path of the saved GeoDataFrame.
    """
    gdf.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="w")
    return filename


def to_geopackage_chunked(gdf: GeoDataFrame, filename: str, chunk_size: int = 1000000) -> str:
    """
    Save GeoDataFrame to a Geopackage file using chunks to help with potential memory consumption.
    This function can potentially be slower than `to_geopackage`, especially if `chunk_size` is not adequately defined.
    Therefore, this function should only be required if `to_geopackage` fails because of memory issues.

    Parameters
    -----------
    gdf : GeoDataFrame
        The GeoDataFrame to save.
    filename : str
        The filename to save to.
    chunk_size : int
        The number of rows per chunk.

    Returns
    --------
    str:
        file path of the saved GeoDataFrame.
    """
    filename_path = Path(filename)
    if filename_path.exists():
        filename_path.unlink()

    chunk = gdf.iloc[0:chunk_size]
    chunk.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="w")

    for i in range(chunk_size, len(gdf), chunk_size):
        chunk = gdf.iloc[i : i + chunk_size]
        chunk.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="a")

    return filename
