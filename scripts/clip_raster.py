import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

import geopandas
import rasterio
from rasterio.mask import mask

from geospatial_tools import DATA_DIR
from geospatial_tools.utils import create_logger

S2_DATA_BASE_PATH = DATA_DIR / "sentinel-2"
S2_10SGD_FILE = S2_DATA_BASE_PATH / "S2B_MSIL2A_20220615T183919_R070_T10SGD_20220618T184146_reprojected.tif"
S2_10SGE_FILE = S2_DATA_BASE_PATH / "S2B_MSIL2A_20220615T183919_R070_T10SGE_20220618T191736_reprojected.tif"
S2_10SGE_VECTOR_TILES = S2_DATA_BASE_PATH / "usa_land_polygon_grid_800m_10SGE.gpkg"
S2_10SGD_VECTOR_TILES = S2_DATA_BASE_PATH / "usa_land_polygon_grid_800m_10SDG.gpkg"

LOGGER = create_logger(__name__)


def clip_process(raster_image, id_polygon, s2_tile_id, output_path):
    try:
        polygon_id, polygon = id_polygon
        with rasterio.open(raster_image) as src:
            out_image, out_transform = mask(src, [polygon], crop=True)
            out_meta = src.meta.copy()
        out_meta.update(
            {"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform}
        )
        output_file = output_path / f"{s2_tile_id}_clipped_{polygon_id}.tif"
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)

        return polygon_id, polygon
    except Exception as e:  # pylint: disable=broad-exception-caught
        return str(e)


def clip_raster_with_polygon(
    raster_image, polygon_layer, s2_tile_id, output_path=S2_DATA_BASE_PATH, num_processes=None, logger=LOGGER
):
    workers = cpu_count()
    if num_processes:
        workers = num_processes

    logger.info(f"Number of workers used: {workers}")

    gdf = geopandas.read_file(polygon_layer)
    polygons = gdf["geometry"]
    ids = gdf.index

    logger.info(f"Output path : [{output_path}]")
    id_polygon_list = zip(ids, polygons)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(clip_process, raster_image, polygon_tuple, s2_tile_id, output_path)
            for polygon_tuple in id_polygon_list
        ]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    for result in results:
        logger.info(f"Writing file successful : [{result}]")


if __name__ == "__main__":
    clip_raster_with_polygon(
        S2_10SGE_FILE,
        S2_10SGE_VECTOR_TILES,
        "S2B_MSIL2A_20220615T183919_R070_T10SGE_20220618T191736",
    )  # pylint: disable=no-value-for-parameter
