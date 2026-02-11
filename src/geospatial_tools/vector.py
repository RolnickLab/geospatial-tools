"""This module contains functions that process or create vector data."""

import logging
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path

import dask_geopandas as dgpd
import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas import GeoDataFrame
from numpy import ndarray
from shapely import Polygon

from geospatial_tools.utils import GEOPACKAGE_DRIVER, create_crs, create_logger

LOGGER = create_logger(__name__)


def create_grid_coordinates(
    bounding_box: list | tuple, grid_size: float, logger: logging.Logger = LOGGER
) -> tuple[ndarray, ndarray]:
    """
    Create grid coordinates based on input bounding box and grid size.

    Args:
      bounding_box: The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
        Unit needs to be based on projection used (meters, degrees, etc.).
      grid_size: Cell size for grid. Unit needs to be based on projection used (meters, degrees, etc.).
      logger: Logger instance.

    Returns:
    """
    logger.info(f"Creating grid coordinates for bounding box [{bounding_box}]")
    min_lon, min_lat, max_lon, max_lat = bounding_box
    lon_coords = np.arange(min_lon, stop=max_lon, step=grid_size)
    lat_coords = np.arange(min_lat, stop=max_lat, step=grid_size)
    return lon_coords, lat_coords


def generate_flattened_grid_coords(
    lon_coords: ndarray, lat_coords: ndarray, logger: logging.Logger = LOGGER
) -> tuple[ndarray, ndarray]:
    """
    Takes in previously created grid coordinates and flattens them.

    Args:
      lon_coords: Longitude grid coordinates
      lat_coords: Latitude grid coordinates
      logger: Logger instance.

    Returns:
    """

    logger.info("Creating flattened grid coordinates")
    lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)
    lon_grid = lon_grid.flatten()
    lat_grid = lat_grid.flatten()
    return lon_grid, lat_grid


def _create_polygons_from_coords_chunk(chunk: tuple[ndarray, ndarray, float]) -> list[Polygon]:
    """
    Helper function to create polygons from input coordinates chunk.

    Args:
      chunk: Coordinates chunk as a tuple (longitude coords, latitude coords, grid size).

    Returns:
    """
    lon_coords, lat_coords, grid_size = chunk
    polygons = []
    for lon, lat in zip(lon_coords, lat_coords, strict=False):
        polygons.append(
            Polygon([(lon, lat), (lon + grid_size, lat), (lon + grid_size, lat + grid_size), (lon, lat + grid_size)])
        )
    return polygons


def create_vector_grid(
    bounding_box: list | tuple, grid_size: float, crs: str = None, logger: logging.Logger = LOGGER
) -> GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size. This function uses NumPy vectorized arrays for
    optimized performance.

    Args:
      bounding_box: The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
      grid_size: The size of each grid cell in degrees.
      crs: CRS code for projection. ex. 'EPSG:4326'
      logger: Logger instance.

    Returns:
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
    _generate_uuid_column(grid)
    return grid


def create_vector_grid_parallel(
    bounding_box: list | tuple | ndarray,
    grid_size: float,
    crs: str | int = None,
    num_of_workers: int = None,
    logger: logging.Logger = LOGGER,
) -> GeoDataFrame:
    """
    Create a grid of polygons within the specified bounds and cell size. This function uses NumPy for optimized
    performance and ProcessPoolExecutor for parallel execution.

    Args:
      bounding_box: The bounding box of the grid as (min_lon, min_lat, max_lon, max_lat).
      grid_size: The size of each grid cell in degrees.
      crs: Coordinate reference system for the resulting GeoDataFrame.
      num_of_workers: The number of processes to use for parallel execution. Defaults to the min of number of CPU cores
        or number of cells in the grid
      logger: Logger instance.

    Returns:
    """
    lon_coords, lat_coords = create_grid_coordinates(bounding_box=bounding_box, grid_size=grid_size, logger=logger)
    lon_flat_grid, lat_flat_grid = generate_flattened_grid_coords(
        lat_coords=lat_coords, lon_coords=lon_coords, logger=logger
    )

    num_cells = len(lon_flat_grid)
    workers = min(cpu_count(), num_cells)
    if num_of_workers:
        workers = num_of_workers

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

    logger.info("Managing properties")
    properties = {"data": {"geometry": polygons}}
    if crs:
        projection = create_crs(crs)
        properties["crs"] = projection
    grid: GeoDataFrame = GeoDataFrame(**properties)
    logger.info("Creating spatial index")
    grid.sindex  # pylint: disable=W0104
    logger.info("Generating polygon UUIDs")
    _generate_uuid_column(grid)
    return grid


def _generate_uuid_column(df, column_name: str = "feature_id") -> None:
    """

    Args:
      df:
      column_name:

    Returns:


    """
    df[column_name] = [str(uuid.uuid4()) for _ in range(len(df))]


def dask_spatial_join(
    select_features_from: GeoDataFrame,
    intersected_with: GeoDataFrame,
    join_type: str = "inner",
    predicate: str = "intersects",
    num_of_workers: int = 4,
) -> GeoDataFrame:
    """

    Args:
      select_features_from:
      intersected_with:
      join_type: str:
      predicate: str:
      num_of_workers:

    Returns:


    """
    dask_select_gdf = dgpd.from_geopandas(select_features_from, npartitions=num_of_workers)
    dask_intersected_gdf = dgpd.from_geopandas(intersected_with, npartitions=1)
    result = dgpd.sjoin(dask_select_gdf, dask_intersected_gdf, how=join_type, predicate=predicate).compute()
    result = GeoDataFrame(result)
    result.sindex  # pylint: disable=W0104

    return result


def multiprocessor_spatial_join(
    select_features_from: GeoDataFrame,
    intersected_with: GeoDataFrame,
    join_type: str = "inner",
    predicate: str = "intersects",
    num_of_workers: int = 4,
    logger: logging.Logger = LOGGER,
) -> GeoDataFrame:
    """

    Args:
      select_features_from: Numpy array containing the polygons from which to select features from.
      intersected_with: Geodataframe containing the polygons that will be used to select features with via an
        intersect operation.
      join_type: How the join will be executed. Available join_types are:
        ['left', 'right', 'inner']. Defaults to 'inner'
      predicate: The predicate to use for selecting features from. Available predicates are:
        ['intersects', 'contains', 'within', 'touches', 'crosses', 'overlaps']. Defaults to 'intersects'
      num_of_workers: The number of processes to use for parallel execution. Defaults to 4.
      logger: Logger instance.

    Returns:


    """
    select_features_from_chunks = np.array_split(select_features_from, num_of_workers)
    with ProcessPoolExecutor(max_workers=num_of_workers) as executor:
        futures = [
            executor.submit(gpd.sjoin, chunk, intersected_with, how=join_type, predicate=predicate)
            for chunk in select_features_from_chunks
        ]
        intersecting_polygons_list = [future.result() for future in futures]
    logger.info("Concatenating results")
    intersecting_polygons = gpd.GeoDataFrame(pd.concat(intersecting_polygons_list, ignore_index=True))
    logger.info("Creating spatial index")
    intersecting_polygons.sindex  # pylint: disable=W0104
    if len(intersected_with) > 1:
        # This last step is necessary when doing a spatial join where `intersected_with` contains multiple features
        logger.info("Dropping duplicates")
        intersecting_polygons = intersecting_polygons.drop_duplicates(subset="geometry")
    return intersecting_polygons


def select_polygons_by_location(
    select_features_from: GeoDataFrame,
    intersected_with: GeoDataFrame,
    num_of_workers: int = None,
    join_type: str = "inner",
    predicate: str = "intersects",
    join_function=multiprocessor_spatial_join,
    logger: logging.Logger = LOGGER,
) -> GeoDataFrame:
    """
    This function executes a `select by location` operation on a GeoDataFrame. It is essentially a wrapper around
    `gpd.sjoin` to allow parallel execution. While it does use `sjoin`, only the columns from `select_features_from` are
    kept.

    Args:
      select_features_from: GeoDataFrame containing the polygons from which to select features from.
      intersected_with: Geodataframe containing the polygons that will be used to select features with via an intersect
        operation.
      num_of_workers: Number of parallel processes to use for execution. If using
        on a compute cluster, please set a specific amount (ex. 1 per CPU core requested).
        Defaults to the min of number of CPU cores
        or number (cpu_count())
      join_type:
      predicate: The predicate to use for selecting features from. Available predicates are:
        ['intersects', 'contains', 'within', 'touches', 'crosses', 'overlaps']. Defaults to 'intersects'
      join_function: Function that will execute the join operation. Available functions are:
        'multiprocessor_spatial_join'; 'dask_spatial_join'; or custom functions.
        (Default value = multiprocessor_spatial_join)
      logger: Logger instance.

    Returns:
    """
    workers = cpu_count()
    if num_of_workers:
        workers = num_of_workers
    logger.info(f"Number of workers used: {workers}")

    intersecting_polygons = join_function(
        select_features_from=select_features_from,
        intersected_with=intersected_with,
        join_type=join_type,
        predicate=predicate,
        num_of_workers=num_of_workers,
    )
    logger.info("Filtering columns of the results")
    filtered_result_gdf = intersecting_polygons.drop(columns=intersecting_polygons.filter(like="_right").columns)
    column_list_to_filter = [item for item in intersected_with.columns if item not in select_features_from.columns]
    conserved_columns = [col for col in filtered_result_gdf.columns if col not in column_list_to_filter]
    filtered_result_gdf = filtered_result_gdf[conserved_columns]  # pylint: disable=E1136

    return filtered_result_gdf


def to_geopackage(gdf: GeoDataFrame, filename: str | Path, logger=LOGGER) -> str:
    """
    Save GeoDataFrame to a Geopackage file.

    Args:
      gdf: The GeoDataFrame to save.
      filename: The filename to save to.
      logger: Logger instance (Default value = LOGGER)

    Returns:
    """
    start = time.time()
    logger.info("Starting writing process")
    if isinstance(gdf, pd.DataFrame):
        gdf = GeoDataFrame(gdf)
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

    Args:
      gdf: The GeoDataFrame to save.
      filename: The filename to save to.
      chunk_size: The number of rows per chunk.
      logger: Logger instance.

    Returns:
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

    Args:
      polygon_feature: Polygon feature that will be used to find which features of `vector_features` are contained
        within it. In this function, it is expected to be a GeoSeries, so a single row from a GeoDataFrame.
      vector_features: The dataframe containing the features that will be grouped by polygon_feature.

    Returns:
    """
    contained_features = vector_features[vector_features.within(polygon_feature.geometry)]
    return contained_features


def add_and_fill_contained_column(
    polygon_feature, polygon_column_name: str, vector_features, vector_column_name: str, logger=LOGGER
) -> None:
    """
    This function make in place changes to `vector_geodataframe`.

    The purpose of this function is to first do a spatial search operation on which `vector_features` are within
    `polygon_feature`, and then write the contents found in the `polygon_column_name` to the selected `vector_features`

    Args:
      polygon_feature: Polygon feature that will be used to find which features of `vector_features` are contained
        within it.
      polygon_column_name: The name of the column in `polygon_feature` that contains the name/id of each polygon to
        be written to `vector_features`.
      vector_features: The dataframe containing the features that will be grouped by polygon_feature.
      vector_column_name: The name of the column in `vector_features` that will the name/id of each polygon.
      logger: Logger instance

    Returns:
    """
    feature_name = polygon_feature[polygon_column_name]
    logger.info(f"Selecting all vector features that are within {feature_name}")
    selected_features = select_all_within_feature(polygon_feature=polygon_feature, vector_features=vector_features)
    logger.info(f"Writing [{feature_name}] to selected vector features")

    vector_features.loc[selected_features.index, vector_column_name] = vector_features.loc[
        selected_features.index, vector_column_name
    ].apply(lambda s: s | {feature_name})


# Potential outdated function
def find_and_write_all_contained_features(
    polygon_features: gpd.GeoDataFrame,
    polygon_column: str,
    vector_features: gpd.GeoDataFrame,
    vector_column_name: str,
    logger=LOGGER,
) -> None:
    """
    This function make in place changes to `vector_geodataframe`.

    It iterates on all features of a dataframe containing polygons and executes a spatial search with each
    polygon to find all vector features from `vector_features` that are contained by it.

    The name/id of each polygon is added to a set in a new column in
    `vector_features` to identify which features are within which polygon.

    To make things simple, this is basically a "group by" operation based on the
    "within" spatial operator. Each feature in `vector_features` will have a list of
    all the polygons that contain it (contain as being completely within the polygon).

    Args:
      polygon_features: Dataframes containing polygons. Will be used to find which features of `vector_features`
        are contained within which polygon
      polygon_column: The name of the column in `polygon_features` that contains the name/id
        of each polygon.
      vector_features: The dataframe containing the features that will be grouped by polygon.
      vector_column_name: The name of the column in `vector_features` that will the name/id of each polygon.
      logger:  (Default value = LOGGER)

    Returns:
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
    vector_features[vector_column_name] = vector_features[vector_column_name].apply(sorted)
    logger.info("Process to find and identify contained features is completed")


def spatial_join_within(
    polygon_features: gpd.GeoDataFrame,
    polygon_column: str,
    vector_features: gpd.GeoDataFrame,
    vector_column_name: str,
    join_type: str = "left",
    predicate: str = "within",
    logger=LOGGER,
) -> gpd.GeoDataFrame:
    """
    This function does approximately the same thing as `find_and_write_all_contained_features`, but does not make in
    place changes to `vector_features` and instead returns a new dataframe.

    This function is more efficient than `find_and_write_all_contained_features` but offers less flexibility.

    It does a spatial join based on a within operation between features to associate which `vector_features`
    are within which `polygon_features`, groups the results by vector feature

    Args:
      polygon_features: Dataframes containing polygons. Will be used to find which features of `vector_features`
        are contained within which polygon
      polygon_column: The name of the column in `polygon_features` that contains the name/id
        of each polygon.
      vector_features: The dataframe containing the features that will be grouped by polygon.
      vector_column_name: The name of the column in `vector_features` that will contain the name/id of each polygon.
      join_type:
      predicate: The predicate to use for the spatial join operation. Defaults to `within`.
      logger: Logger instance

    Returns:
    """
    temp_feature_id = "feature_id"
    uuid_suffix = str(uuid.uuid4())
    if temp_feature_id in vector_features.columns:
        logger.info("Creating temporary UUID field for join operations")
        temp_feature_id = f"{temp_feature_id}_{uuid_suffix}"
    _generate_uuid_column(df=vector_features, column_name=temp_feature_id)
    logger.info("Starting process to find and identify contained features using spatial 'within' join operation")
    joined_gdf = gpd.sjoin(
        vector_features, polygon_features[[polygon_column, "geometry"]], how=join_type, predicate=predicate
    )
    logger.info("Grouping results")
    grouped_gdf = joined_gdf.groupby(temp_feature_id)[polygon_column].agg(list).reset_index()
    logger.info("Cleaning and merging results")
    features = vector_features.merge(grouped_gdf, on=temp_feature_id, how="left")
    features = features.rename(columns={polygon_column: vector_column_name})
    features.drop(columns=[temp_feature_id], inplace=True)
    features[vector_column_name] = features[vector_column_name].apply(sorted)
    logger.info("Spatial join operation is completed")
    return gpd.GeoDataFrame(features)
