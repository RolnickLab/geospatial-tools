"""This module contains functions that process or create raster/image data."""

import concurrent.futures
import logging
import pathlib
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from typing import Union

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
    target_crs
        EPSG code in string or int format. Can be given in the following ways: 5070 | "5070" | "EPSG:5070"
    target_path
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


def clip_process(
    raster_image: Union[pathlib.Path, str],
    id_polygon: tuple[int, GeoDataFrame],
    s2_tile_id: str,
    output_path: Union[pathlib.Path, str],
):
    try:
        polygon_id, polygon = id_polygon
        with rasterio.open(raster_image) as src:
            out_image, out_transform = mask(src, [polygon], crop=True)
            out_meta = src.meta.copy()
        out_meta.update(
            {"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform}
        )
        if isinstance(output_path, str):
            output_path = pathlib.Path(output_path)
        output_file = output_path / f"{s2_tile_id}_clipped_{polygon_id}.tif"
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)

        return polygon_id, polygon
    except Exception as e:  # pylint: disable=broad-exception-caught
        return str(e)


def clip_raster_with_polygon(
    raster_image: Union[pathlib.Path, str],
    polygon_layer: Union[pathlib.Path, str, GeoDataFrame],
    s2_tile_id: str,
    output_path: Union[str, pathlib.Path] = DATA_DIR,
    num_of_workers: int = None,
    logger: logging.Logger = LOGGER,
):
    workers = cpu_count()
    if num_of_workers:
        workers = num_of_workers

    logger.info(f"Number of workers used: {workers}")
    logger.info(f"Output path : [{output_path}]")

    if isinstance(output_path, str):
        output_path = pathlib.Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    gdf = polygon_layer
    if not isinstance(polygon_layer, GeoDataFrame):
        gdf = gpd.read_file(polygon_layer)

    polygons = gdf["geometry"]
    ids = gdf.index

    id_polygon_list = zip(ids, polygons)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(clip_process, raster_image, polygon_tuple, s2_tile_id, output_path)
            for polygon_tuple in id_polygon_list
        ]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    for result in results:
        logger.info(f"Writing file successful : [{result}]")
