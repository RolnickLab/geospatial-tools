from geospatial_tools import DATA_DIR, PROJECT_ROOT
from geospatial_tools.raster import clip_raster_with_polygon
from geospatial_tools.utils import create_logger

S2_DATA_BASE_PATH = DATA_DIR / "sentinel-2"
S2_10SGD_FILE = S2_DATA_BASE_PATH / "S2B_MSIL2A_20220615T183919_R070_T10SGD_20220618T184146_reprojected.tif"
S2_10SGE_FILE = S2_DATA_BASE_PATH / "S2B_MSIL2A_20220615T183919_R070_T10SGE_20220618T191736_reprojected.tif"
S2_10SGE_VECTOR_TILES = S2_DATA_BASE_PATH / "usa_land_polygon_grid_800m_10SGE.gpkg"
S2_10SGD_VECTOR_TILES = S2_DATA_BASE_PATH / "usa_land_polygon_grid_800m_10SDG.gpkg"

RASTER = PROJECT_ROOT / "notebooks/S2A_MSIL2A_20240705T185921_R013_T10SDJ_20240706T050346_reprojected.tif"
POLYGON = DATA_DIR / "vector_tiles_with_s2tiles_subset.gpkg"
S2_ID = "S2A_MSIL2A_20240705T185921_R013_T10SDJ_20240706T050346"
LOGGER = create_logger(__name__)


if __name__ == "__main__":
    clip_raster_with_polygon(
        RASTER,
        S2_10SGE_VECTOR_TILES,
        S2_ID,
    )  # pylint: disable=no-value-for-parameter
