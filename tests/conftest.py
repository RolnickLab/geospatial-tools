import geopandas as gpd
import numpy as np
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
from shapely import box


@pytest.fixture
def test_raster(tmp_path):
    """Fixture to create a test raster file."""
    # Raster parameters
    width = 100
    height = 100
    pixel_size = 1.0
    x_min = 0.0
    y_max = 100.0
    crs = CRS.from_epsg(4326)
    transform = from_origin(x_min, y_max, pixel_size, pixel_size)
    rng = np.random.default_rng(seed=42)
    data = rng.random((height, width))

    raster_path = tmp_path / "test_raster.tif"
    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    yield raster_path


@pytest.fixture
def polygon_layer():
    minx, miny, maxx, maxy = 20, 20, 80, 80
    polygon = box(minx, miny, maxx, maxy)
    gdf = gpd.GeoDataFrame({"geometry": [polygon]}, crs="EPSG:4326")

    yield gdf


@pytest.fixture
def three_polygons_layer():
    minx_1, miny_1, maxx_1, maxy_1 = 10, 10, 20, 20
    minx_2, miny_2, maxx_2, maxy_2 = 30, 30, 40, 40
    minx_3, miny_3, maxx_3, maxy_3 = 50, 50, 60, 60

    polygon_1 = box(minx_1, miny_1, maxx_1, maxy_1)
    polygon_2 = box(minx_2, miny_2, maxx_2, maxy_2)
    polygon_3 = box(minx_3, miny_3, maxx_3, maxy_3)

    gdf = gpd.GeoDataFrame({"geometry": [polygon_1, polygon_2, polygon_3]}, crs="EPSG:4326")

    yield gdf
