"""This module contains functions that process or create raster/image data."""

import concurrent.futures
import logging
import pathlib
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from typing import Optional, Union

import geopandas as gpd
import rasterio
from geopandas import GeoDataFrame
from rasterio.mask import mask
from rasterio.warp import Resampling, calculate_default_transform, reproject

from geospatial_tools import DATA_DIR
from geospatial_tools.utils import create_crs, create_logger

LOGGER = create_logger(__name__)


def reproject_raster(
    dataset_path: Union[str, pathlib.Path],
    target_crs: Union[str, int],
    target_path: Union[str, pathlib.Path],
    logger: logging.Logger = LOGGER,
):
    """

    Parameters
    ----------
    dataset_path
        Path to the dataset to be reprojected.
    target_crs
        EPSG code in string or int format. Can be given in the following ways: 5070 | "5070" | "EPSG:5070"
    target_path
        Path and filename for reprojected dataset.
    logger

    Returns
    -------

    """
    if isinstance(dataset_path, str):
        dataset_path = pathlib.Path(dataset_path)

    if isinstance(target_path, str):
        target_path = pathlib.Path(target_path)

    target_crs = create_crs(target_crs, logger=logger)

    with rasterio.open(dataset_path) as source_dataset:
        transform, width, height = calculate_default_transform(
            source_dataset.crs, target_crs, source_dataset.width, source_dataset.height, *source_dataset.bounds
        )
        kwargs = source_dataset.meta.copy()
        kwargs.update({"crs": target_crs, "transform": transform, "width": width, "height": height})

        with rasterio.open(target_path, "w", **kwargs) as reprojected_dataset:
            for i in range(1, source_dataset.count + 1):
                reproject(
                    source=rasterio.band(source_dataset, i),
                    destination=rasterio.band(reprojected_dataset, i),
                    src_transform=source_dataset.transform,
                    src_crs=source_dataset.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest,
                )
    if target_path.exists():
        logger.info(f"Reprojected file created at {target_path}")
        return target_path


def _clip_process(
    raster_image: Union[pathlib.Path, str],
    id_polygon: tuple[int, GeoDataFrame],
    base_output_filename: Optional[str],
    output_dir: Union[pathlib.Path, str],
) -> Union[tuple[int, GeoDataFrame, pathlib.Path], str]:
    """

    Parameters
    ----------
    raster_image
        Path to raster image to be clipped.
    id_polygon
        Tuple containing an id number and a polygon (row from a Geodataframe).
    base_output_filename
        Base filename for outputs. If `None`, will be taken from input polygon layer.
    output_dir
        Directory path where output will be written.

    Returns
    -------
    Tuple
        Tuple containing an id number and a polygon in Geodataframe format.

    """
    polygon_id, polygon = id_polygon
    try:
        with rasterio.open(raster_image) as src:
            out_image, out_transform = mask(src, [polygon], crop=True)
            out_meta = src.meta.copy()
        out_meta.update(
            {"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform}
        )
        if isinstance(output_dir, str):
            output_dir = pathlib.Path(output_dir)
        output_file = output_dir / f"{base_output_filename}_clipped_{polygon_id}.tif"
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)

        return polygon_id, polygon, output_file
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Polygon ID: {polygon_id}\nPolygon: {polygon}\nError message: {str(e)}"


def clip_raster_with_polygon(
    raster_image: Union[pathlib.Path, str],
    polygon_layer: Union[pathlib.Path, str, GeoDataFrame],
    base_output_filename: Optional[str] = None,
    output_dir: Union[str, pathlib.Path] = DATA_DIR,
    num_of_workers: Optional[int] = None,
    logger: logging.Logger = LOGGER,
) -> list[pathlib.Path]:
    """

    Parameters
    ----------
    raster_image
        Path to raster image to be clipped.
    polygon_layer
        Polygon layer which polygons will be used to clip the raster image.
    base_output_filename
        Base filename for outputs. If `None`, will be taken from input polygon layer.
    output_dir
        Directory path where output will be written.
    num_of_workers
        The number of processes to use for parallel execution. Defaults to `cpu_count()`.
    logger
        Logger instance

    Returns
    -------
    List
        List of clipped rasters.

    """
    workers = cpu_count()
    if num_of_workers:
        workers = num_of_workers

    logger.info(f"Number of workers used: {workers}")
    logger.info(f"Output path : [{output_dir}]")

    if isinstance(raster_image, str):
        raster_image = pathlib.Path(raster_image)
    if not raster_image.exists():
        logger.error("Raster image does not exist")
        return []

    if not base_output_filename:
        base_output_filename = raster_image.stem

    if isinstance(output_dir, str):
        output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    gdf = polygon_layer
    if not isinstance(polygon_layer, GeoDataFrame):
        gdf = gpd.read_file(polygon_layer)

    polygons = gdf["geometry"]
    ids = gdf.index

    id_polygon_list = zip(ids, polygons)
    logger.info(f"Clipping raster image with {len(polygons)} polygons")
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_clip_process, raster_image, polygon_tuple, base_output_filename, output_dir)
            for polygon_tuple in id_polygon_list
        ]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    path_list = []
    for result in results:
        if isinstance(result, tuple):
            logger.debug(f"Writing file successful : [{result}]")
            path_list.append(result[2])
        if isinstance(result, str):
            logger.warning(f"There was an error writing the file : [{result}]")
    logger.info("Clipping process finished")
    return path_list
