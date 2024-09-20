import tempfile

import rasterio

from geospatial_tools.raster import clip_raster_with_polygon, reproject_raster


def test_reproject_raster(test_raster):
    with tempfile.NamedTemporaryFile(suffix=".tif") as tmpfile:
        rpj_file = reproject_raster(test_raster, target_crs=5070, target_path=tmpfile.name)
        with rasterio.open(rpj_file) as raster_file:
            assert raster_file.crs == 5070


def test_clip_raster_with_polygon_single_polygon(test_raster, polygon_layer):
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = clip_raster_with_polygon(test_raster, polygon_layer=polygon_layer, output_dir=tmp_dir)
        assert len(output) == 1


def test_clip_raster_with_polygon_three_polygons(test_raster, three_polygons_layer):
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = clip_raster_with_polygon(test_raster, polygon_layer=three_polygons_layer, output_dir=tmp_dir)
        assert len(output) == 3
