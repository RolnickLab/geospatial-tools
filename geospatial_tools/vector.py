"""This module contains functions that process or create vector data."""

import logging
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path
from typing import Union

import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas import GeoDataFrame
from numpy import ndarray
from shapely import Polygon

from geospatial_tools.utils import GEOPACKAGE_DRIVER, create_logger

LOGGER = create_logger(__name__)


def create_grid_coordinates(
    bounding_box: Union[list, tuple], grid_size: float, logger: logging.Logger = LOGGER
) -> tuple[ndarray, ndarray]:
    """
    Create grid coordinates based on input bounding box and grid size.

    Parameters
    -----------
    bounding_box
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
        Unit needs to be based on projection used (meters, degrees, etc.).
    grid_size
        Cell size for grid. Unit needs to be based on projection used (meters, degrees, etc.).
    logger
        Logger instance.

    Returns
    --------
        Tuple containing the longitude and latitude grid coordinates.
    """
    logger.info(f"Creating grid coordinates for bounding box [{bounding_box}]")
    min_lon, min_lat, max_lon, max_lat = bounding_box
    lon_coords = np.arange(start=min_lon, stop=max_lon, step=grid_size)
    lat_coords = np.arange(start=min_lat, stop=max_lat, step=grid_size)
    return lon_coords, lat_coords


def generate_flattened_grid_coords(
    lon_coords: ndarray, lat_coords: ndarray, logger: logging.Logger = LOGGER
) -> tuple[ndarray, ndarray]:
    """
    Takes in previously created grid coordinates and flattens them.

    Parameters
    -----------
    lon_coords
        Longitude grid coordinates
    lat_coords
        Latitude grid coordinates
    logger
        Logger instance.

    Returns
    --------
        Flattened longitude and latitude grids.
    """

    logger.info("Creating flattened grid coordinates")
    lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)
    lon_grid = lon_grid.flatten()
    lat_grid = lat_grid.flatten()
    return lon_grid, lat_grid


def _create_polygons_from_coords_chunk(chunk: tuple[ndarray, ndarray, float]) -> list[Polygon]:
    """
    Helper function to create polygons from input coordinates chunk.

    Parameters
    -----------
    chunk
        Coordinates chunk as a tuple (longitude coords, latitude coords, grid size).

    Returns
    --------
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
    Create a grid of polygons within the specified bounds and cell size. This function uses NumPy vectorized arrays for
    optimized performance.

    Parameters
    -----------
    bounding_box
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size
        The size of each grid cell in degrees.
    crs
        CRS code for projection. ex. 'EPSG:4326'
    logger
        Logger instance.

    Returns
    --------
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
    Create a grid of polygons within the specified bounds and cell size. This function uses NumPy for optimized
    performance and ProcessPoolExecutor for parallel execution.

    Parameters
    -----------
    bounding_box
        The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
    grid_size
        The size of each grid cell in degrees.
    crs
        Coordinate reference system for the resulting GeoDataFrame.
    num_processes
        The number of processes to use for parallel execution. Defaults to the min of number of CPU cores or number
        of cells in the grid
    logger
        Logger instance.

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
    logger.info("Creating polygons from chunks")
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


def _sjoin_chunk(
    select_from_chunk: ndarray, intersect_with_gdf: GeoDataFrame, predicate: str = "intersects"
) -> GeoDataFrame:
    """

    Parameters
    ----------
    select_from_chunk
        Numpy array containing the polygons from which to select features from.
    intersect_with_gdf
        Geodataframe containing the polygons that will be used to select features with via an intersect operation.
    predicate
        The predicate to use for selecting features from. Available predicates are:
        ['intersects', 'contains', 'within', 'touches', 'crosses', 'overlaps']. Defaults to 'intersects'

    Returns
    -------
        A GeoDataFrame containing the selected polygons.
    """
    return gpd.sjoin(select_from_chunk, intersect_with_gdf, how="inner", predicate=predicate)


def select_polygons_by_location(
    select_features_from_gdf: GeoDataFrame,
    intersect_with_gdf: GeoDataFrame,
    num_processes: int = None,
    predicate="intersects",
    logger: logging.Logger = LOGGER,
) -> GeoDataFrame:
    """
    This function executes a `select by location` operation on a GeoDataFrame. It is essentially a wrapper around
    `gpd.sjoin` to allow parallel execution.

    Parameters
    ----------
    select_features_from_gdf
        GeoDataFrame containing the polygons from which to select features from.
    intersect_with_gdf
        Geodataframe containing the polygons that will be used to select features with via an intersect operation.
    num_processes
        Number of parallel processes to use for execution. Defaults to the min of number of CPU cores or number
        (cpu_count())
    predicate
        The predicate to use for selecting features from. Available predicates are:
        ['intersects', 'contains', 'within', 'touches', 'crosses', 'overlaps']. Defaults to 'intersects'
    logger
        Logger instance.

    Returns
    -------
    GeoDataFrame:
        A GeoDataFrame containing the selected polygons.
    """
    workers = cpu_count()
    if num_processes:
        workers = num_processes
    logger.info(f"Number of workers used: {workers}")

    select_features_from_chunks = np.array_split(select_features_from_gdf, workers)
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                _sjoin_chunk, select_from_chunk=chunk, intersect_with_gdf=intersect_with_gdf, predicate=predicate
            )
            for chunk in select_features_from_chunks
        ]
        intersecting_polygons_list = [future.result() for future in futures]

    intersecting_polygons = gpd.GeoDataFrame(pd.concat(intersecting_polygons_list, ignore_index=True))
    intersecting_polygons.sindex  # pylint: disable=W0104

    return intersecting_polygons


def to_geopackage(gdf: GeoDataFrame, filename: str, logger=LOGGER) -> str:
    """
    Save GeoDataFrame to a Geopackage file.

    Parameters
    -----------
    gdf
        The GeoDataFrame to save.
    filename
        The filename to save to.
    logger
        Logger instance

    Returns
    --------
        File path of the saved GeoDataFrame.
    """
    start = time.time()
    logger.info("Starting writing process")
    gdf.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="w")
    stop = time.time()
    logger.info(f"File [{filename}] took {stop - start} seconds to write.")

    return filename


def to_geopackage_chunked(
    gdf: GeoDataFrame, filename: str, chunk_size: int = 1000000, logger: logging.Logger = LOGGER
) -> str:
    """
    Save GeoDataFrame to a Geopackage file using chunks to help with potential memory consumption. This function can
    potentially be slower than `to_geopackage`, especially if `chunk_size` is not adequately defined. Therefore, this
    function should only be required if `to_geopackage` fails because of memory issues.

    Parameters
    -----------
    gdf
        The GeoDataFrame to save.
    filename
        The filename to save to.
    chunk_size
        The number of rows per chunk.
    logger
        Logger instance.

    Returns
    --------
        File path of the saved GeoDataFrame.
    """
    filename_path = Path(filename)
    if filename_path.exists():
        filename_path.unlink()

    start = time.time()
    logger.info("Starting writing process")
    logger.info(f"Chunk size used : [{chunk_size}]")
    chunk = gdf.iloc[0:chunk_size]
    chunk.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="w")

    for i in range(chunk_size, len(gdf), chunk_size):
        chunk = gdf.iloc[i : i + chunk_size]
        chunk.to_file(filename, driver=GEOPACKAGE_DRIVER, mode="a")

    stop = time.time()
    logger.info(f"File [{filename}] took {stop - start} seconds to write.")

    return filename


def select_all_within_feature(polygon_feature: gpd.GeoSeries, vector_features: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """
    This function is quite small and simple, but exists mostly as a.

    Parameters
    ----------
    polygon_feature
        Polygon feature that will be used to find which features of `vector_features` are contained within it.
        In this function, it is expected to be a GeoSeries, so a single row from a GeoDataFrame.
    vector_features
        vector_features
        The dataframe containing the features that will be grouped by polygon_feature.

    Returns
    -------
        GeoSeries representing the selected features from `vector_features`
    """
    contained_features = vector_features[vector_features.within(polygon_feature.geometry)]
    return contained_features


def add_and_fill_contained_column(
    polygon_feature, polygon_column_name, vector_features, vector_column_name, logger=LOGGER
):
    """
    This function make in place changes to `vector_geodataframe`.

    The purpose of this function is to first do a spatial search operation on which `vector_features` are within
    `polygon_feature`, and then write the contents found in the `polygon_column_name` to the selected `vector_features`

    Parameters
    ----------
    polygon_feature
        Polygon feature that will be used to find which features of `vector_features` are contained within it
    polygon_column_name
        The name of the column in `polygon_feature` that contains the name/id of each polygon to be written to
        `vector_features`.
    vector_features
        The dataframe containing the features that will be grouped by polygon_feature.
    vector_column_name
        The name of the column in `vector_features` that will the name/id of each polygon.
    logger

    Returns
    -------
    """
    feature_name = polygon_feature[polygon_column_name]
    logger.info(f"Selecting all vector features that are within {feature_name}")
    selected_features = select_all_within_feature(polygon_feature=polygon_feature, vector_features=vector_features)
    logger.info(f"Writing [{feature_name}] to selected vector features")
    [vector_features.at[idx, vector_column_name].add(feature_name) for idx in selected_features.index]


def find_and_write_all_contained_features(
    polygon_features: gpd.GeoDataFrame,
    polygon_column: str,
    vector_features: gpd.GeoDataFrame,
    vector_column_name: str,
    logger=LOGGER,
):
    """
    This function make in place changes to `vector_geodataframe`.

    It iterates on all features of a dataframe containing polygons and executes a spatial search with each
    polygon to find all vector features from `vector_features` that are contained by it.

    The name/id of each polygon is added to a set in a new column in
    `vector_features` to identify which features are within which polygon.

    To make things simple, this is basically a "group by" operation based on the
    "within" spatial operator. Each feature in `vector_features` will have a list of
    all the polygons that contain it (contain as being completely within the polygon).

    Parameters
    ----------
    polygon_features
        Dataframes containing polygons. Will be used to find which features of `vector_features`
        are contained within which polygon
    polygon_column
        The name of the column in `polygon_features` that contains the name/id
        of each polygon.
    vector_features
        The dataframe containing the features that will be grouped by polygon.
    vector_column_name
        The name of the column in `vector_features` that will the name/id of each polygon.
    logger

    Returns
    -------
    """
    if vector_column_name not in vector_features.columns:
        vector_features[vector_column_name] = [set() for _ in range(len(vector_features))]

    logger.info("Starting process to find and identify contained features")
    polygon_features.apply(
        lambda row: add_and_fill_contained_column(
            polygon_feature=row,
            polygon_column_name=polygon_column,
            vector_features=vector_features,
            vector_column_name=vector_column_name,
        ),
        axis=1,
    )
    vector_features[vector_column_name] = vector_features[vector_column_name].apply(lambda x: sorted(x))
    logger.info("Process to find and identify contained features is completed")


def spatial_join_within(
    polygon_features: gpd.GeoDataFrame,
    polygon_column: str,
    vector_features: gpd.GeoDataFrame,
    vector_column_name: str,
    predicate: str = "within",
    logger=LOGGER,
) -> gpd.GeoDataFrame:
    """
    This function does approximately the same thing as `find_and_write_all_contained_features`, but does not make in
    place changes to `vector_features` and instead returns a new dataframe.

    This function is more efficient than `find_and_write_all_contained_features` but offers less flexibility.

    It does a spatial join based on a within operation between features to associate which `vector_features`
    are within which `polygon_features`, groups the results by vector feature

    Parameters
    ----------
    polygon_features
        Dataframes containing polygons. Will be used to find which features of `vector_features`
        are contained within which polygon
    polygon_column
        The name of the column in `polygon_features` that contains the name/id
        of each polygon.
    vector_features
        The dataframe containing the features that will be grouped by polygon.
    vector_column_name
        The name of the column in `vector_features` that will the name/id of each polygon.
    predicate
        The predicate to use for the spatial join operation. Defaults to `within`.
    logger
        Logger instance
    Returns
    -------
    """
    logger.info("Creating temporary UUID field for join operations")
    temp_feature_id = "feature_id"
    vector_features[temp_feature_id] = [uuid.uuid4() for _ in range(len(vector_features))]
    logger.info("Starting process to find and identify contained features using spatial 'within' join operation")
    joined_gdf = gpd.sjoin(
        vector_features, polygon_features[[polygon_column, "geometry"]], how="left", predicate=predicate
    )
    logger.info("Grouping results")
    grouped_gdf = joined_gdf.groupby(temp_feature_id)[polygon_column].agg(list).reset_index()
    logger.info("Cleaning and merging results")
    vector_features = vector_features.merge(grouped_gdf, on=temp_feature_id, how="left")
    vector_features = vector_features.rename(columns={polygon_column: vector_column_name})
    vector_features = vector_features.drop(columns=[temp_feature_id])
    vector_features[vector_column_name] = vector_features[vector_column_name].apply(lambda x: sorted(x))
    logger.info("Spatial join operation is completed")
    return vector_features
