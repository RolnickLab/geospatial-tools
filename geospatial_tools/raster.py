"""This module contains functions that process or create raster/image data."""

import concurrent.futures
import logging
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

import geopandas as gpd
import rasterio
from geopandas import GeoDataFrame
from rasterio.mask import mask
from rasterio.warp import Resampling, calculate_default_transform, reproject

from geospatial_tools import DATA_DIR
from geospatial_tools.utils import create_crs, create_logger

LOGGER = create_logger(__name__)


def reproject_raster(
    dataset_path: str | pathlib.Path,
    target_crs: str | int,
    target_path: str | pathlib.Path,
    logger: logging.Logger = LOGGER,
) -> pathlib.Path | None:
    """

    Args:
      dataset_path: Path to the dataset to be reprojected.
      target_crs: EPSG code in string or int format. Can be given in the following ways: 5070 | "5070" | "EPSG:5070"
      target_path: Path and filename for reprojected dataset.
      logger:
      dataset_path: str | pathlib.Path:
      target_crs: str | int:
      target_path: str | pathlib.Path:
      logger: logging.Logger:  (Default value = LOGGER)

    Returns:


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
    logger.error(f"Failed to reproject file {dataset_path}")
    return None


def _clip_process(
    raster_image: pathlib.Path | str,
    id_polygon: tuple[int, GeoDataFrame],
    base_output_filename: str | None,
    output_dir: pathlib.Path | str,
    logger: logging.Logger = LOGGER,
) -> tuple[int, GeoDataFrame, pathlib.Path] | None:
    """

    Args:
      raster_image: Path to raster image to be clipped.
      id_polygon: Tuple containing an id number and a polygon (row from a Geodataframe).
      base_output_filename: Base filename for outputs. If `None`, will be taken from input polygon layer.
      output_dir: Directory path where output will be written.
      raster_image: pathlib.Path | str:
      id_polygon: tuple[int:
      GeoDataFrame]:
      base_output_filename: str | None:
      output_dir: pathlib.Path | str:
      logger: logging.Logger:  (Default value = LOGGER)

    Returns:


    """
    polygon_id, polygon = id_polygon
    max_retries = 3
    delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            with rasterio.open(raster_image) as src:
                out_image, out_transform = mask(src, [polygon], crop=True)
                out_meta = src.meta.copy()
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                }
            )
            if isinstance(output_dir, str):
                output_dir = pathlib.Path(output_dir)
            output_file = output_dir / f"{base_output_filename}_clipped_{polygon_id}.tif"
            logger.debug(f"Attempting to create clip [{output_file}] from {raster_image}")
            with rasterio.open(output_file, "w", **out_meta) as dest:
                dest.write(out_image)

            return polygon_id, polygon, output_file
        except Exception as e:  # pylint: disable=broad-exception-caught
            if attempt < max_retries:
                logger.debug(f"Clip process failed for attempt {attempt}, retrying...")
                time.sleep(delay)
            else:
                logger.warning(
                    f"There was an error writing the file :[Polygon ID: {polygon_id}"
                    f"\nPolygon: {polygon}\nError message: {e!s}]"
                )
    return None


def clip_raster_with_polygon(
    raster_image: pathlib.Path | str,
    polygon_layer: pathlib.Path | str | GeoDataFrame,
    base_output_filename: str | None = None,
    output_dir: str | pathlib.Path = DATA_DIR,
    num_of_workers: int | None = None,
    logger: logging.Logger = LOGGER,
) -> list[pathlib.Path]:
    """

    Args:
      raster_image: Path to raster image to be clipped.
      polygon_layer: Polygon layer which polygons will be used to clip the raster image.
      base_output_filename: Base filename for outputs. If `None`, will be taken from input polygon layer.
      output_dir: Directory path where output will be written.
      num_of_workers: The number of processes to use for parallel execution. Defaults to `cpu_count()`.
      logger: Logger instance
      raster_image: pathlib.Path | str:
      polygon_layer: pathlib.Path | str | GeoDataFrame:
      base_output_filename: str | None:  (Default value = None)
      output_dir: str | pathlib.Path:  (Default value = DATA_DIR)
      num_of_workers: int | None:  (Default value = None)
      logger: logging.Logger:  (Default value = LOGGER)

    Returns:


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

    id_polygon_list = zip(ids, polygons, strict=False)
    logger.info(f"Clipping raster image with {len(polygons)} polygons")
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                _clip_process,
                raster_image=raster_image,
                id_polygon=polygon_tuple,
                base_output_filename=base_output_filename,
                output_dir=output_dir,
                logger=logger,
            )
            for polygon_tuple in id_polygon_list
        ]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    path_list = []
    for result in results:
        if isinstance(result, tuple):
            logger.debug(f"Writing file successful : [{result}]")
            path_list.append(result[2])
    logger.info("Clipping process finished")
    return path_list


def get_total_band_count(raster_file_list: list[pathlib.Path | str], logger: logging.Logger = LOGGER) -> int:
    """

    Args:
      raster_file_list: List of raster files to be processed.
      logger: Logger instance
      raster_file_list: list[pathlib.Path | str]:
      logger: logging.Logger:  (Default value = LOGGER)

    Returns:


    """
    total_band_count = 0
    for raster in raster_file_list:
        with rasterio.open(raster, "r") as raster_image:
            total_band_count += raster_image.count
    logger.info(f"Calculated a total of [{total_band_count}] bands")
    return total_band_count


def create_merged_raster_bands_metadata(
    raster_file_list: list[pathlib.Path | str], logger: logging.Logger = LOGGER
) -> dict:
    """

    Args:
      raster_file_list:
      logger:
      raster_file_list: list[pathlib.Path | str]:
      logger: logging.Logger:  (Default value = LOGGER)

    Returns:


    """
    logger.info("Creating merged asset metadata")
    total_band_count = get_total_band_count(raster_file_list)
    with rasterio.open(raster_file_list[0]) as meta_source:
        meta = meta_source.meta
        meta.update(count=total_band_count)
    return meta


def merge_raster_bands(
    raster_file_list: list[pathlib.Path | str],
    merged_filename: pathlib.Path | str,
    merged_band_names: list[str] = None,
    merged_metadata: dict = None,
    logger: logging.Logger = LOGGER,
) -> pathlib.Path | None:
    """
    This function aims to combine multiple overlapping raster bands into a single raster image.

    Example use case: I have 3 bands, B0, B1 and B2, each as an independent raster file (like is the case with
    downloaded STAC data.

    While it can probably be used to create spatial time series, and not just combine bands
    from a single image product, it has not yet been tested for that specific purpose.

    Args:
      raster_file_list: List of raster files to be processed.
      merged_filename: Name of output raster file.
      merged_metadata: Dictionary of metadata to use if you prefer to great it independently.
      merged_band_names: Names of final output raster bands. For example : I have 3 images representing each
    a single band; raster_file_list =  ["image01_B0.tif", "image01_B1.tif", "image01_B2.tif"].
    With, merged_band_names, individual band id can be assigned for the final output raster;
    ["B0", "B1", "B2"].
      logger: Logger instance
      raster_file_list: list[pathlib.Path | str]:
      merged_filename: pathlib.Path | str:
      merged_band_names: list[str]:  (Default value = None)
      merged_metadata: dict:  (Default value = None)
      logger: logging.Logger:  (Default value = LOGGER)

    Returns:
    """
    if not merged_metadata:
        merged_metadata = create_merged_raster_bands_metadata(raster_file_list)

    merged_image_index = 1
    band_names_index = 0

    logger.info(f"Merging asset [{merged_filename}] ...")
    # Create the final raster image in which all bands will be written to
    with rasterio.open(merged_filename, "w", **merged_metadata) as merged_asset_image:
        # Iterate through the raster file list to be merged
        for raster_file in raster_file_list:
            asset_name = pathlib.Path(raster_file).name
            logger.info(f"Writing band image: {asset_name}")
            with rasterio.open(raster_file) as source_image:
                num_of_bands = source_image.count

                # Iterate through each band of the raster file
                for source_image_band_index in range(1, num_of_bands + 1):
                    logger.info(
                        f"Writing asset sub item band {source_image_band_index} "
                        f"to merged index band {merged_image_index}"
                    )
                    # Write band to output merged_asset_image
                    merged_asset_image.write_band(merged_image_index, source_image.read(source_image_band_index))
                    _handle_band_metadata(
                        source_image=source_image,
                        source_image_band_index=source_image_band_index,
                        band_names_index=band_names_index,
                        merged_asset_image=merged_asset_image,
                        merged_band_names=merged_band_names,
                        merged_image_index=merged_image_index,
                    )
                    merged_image_index += 1
                band_names_index += 1

    if not merged_filename.exists():
        return None

    return merged_filename


def _handle_band_metadata(
    source_image: rasterio.io.DatasetReader,
    source_image_band_index: int,
    band_names_index: int,
    merged_asset_image: rasterio.io.DatasetWriter,
    merged_band_names: list[str],
    merged_image_index: int,
):
    """

    Args:
      source_image: rasterio.io.DatasetReader:
      source_image_band_index: int:
      band_names_index: int:
      merged_asset_image: rasterio.io.DatasetWriter:
      merged_band_names: list[str]:
      merged_image_index: int:

    Returns:


    """
    source_description_index = source_image_band_index - 1
    description = source_image.descriptions[source_description_index]
    num_of_bands = source_image.count
    if merged_band_names:
        description = merged_band_names[band_names_index]
        if num_of_bands > 1:
            description = f"{description}-{source_image_band_index}"
    merged_asset_image.set_band_description(merged_image_index, description)
    merged_asset_image.update_tags(merged_image_index, **source_image.tags(source_image_band_index))
