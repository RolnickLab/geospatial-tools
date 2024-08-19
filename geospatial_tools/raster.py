"""This module contains functions that process or create raster/image data."""

import pathlib
from typing import Union

import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject

from geospatial_tools.utils import create_crs, create_logger

LOGGER = create_logger(__name__)


def reproject_raster(
    dataset_path: Union[str, pathlib.Path],
    target_crs: Union[str, int],
    target_path: Union[str, pathlib.Path],
    logger=LOGGER,
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
