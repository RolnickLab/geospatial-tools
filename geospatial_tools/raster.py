import pathlib
from typing import Union

import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject

from geospatial_tools.utils import create_crs, create_logger

LOGGER = create_logger(__name__)


def reproject_raster(
    source_path: Union[str, pathlib.Path],
    dataset_path: Union[str, pathlib.Path],
    dataset_crs: Union[str, int],
    logger=LOGGER,
):
    """

    Parameters
    ----------
    source_path
    dataset_path
    dataset_crs : Union[str, int]
        EPSG code in string or int format. Can be given in the following ways: 5070 | "5070" | "EPSG:5070"
    logger

    Returns
    -------

    """
    if isinstance(source_path, str):
        source_path = pathlib.Path(source_path)

    if isinstance(dataset_path, str):
        dataset_path = pathlib.Path(dataset_path)

    target_crs = create_crs(dataset_crs)

    with rasterio.open(source_path) as source:
        transform, width, height = calculate_default_transform(
            source.crs, target_crs, source.width, source.height, *source.bounds
        )
        kwargs = source.meta.copy()
        kwargs.update({"crs": dataset_crs, "transform": transform, "width": width, "height": height})

        with rasterio.open(dataset_path, "w", **kwargs) as dataset:
            for i in range(1, source.count + 1):
                reproject(
                    source=rasterio.band(source, i),
                    destination=rasterio.band(dataset, i),
                    src_transform=source.transform,
                    src_crs=source.crs,
                    dst_transform=transform,
                    dst_crs=dataset_crs,
                    resampling=Resampling.nearest,
                )
    logger.info(f"Reprojected file created at {dataset_path}")
