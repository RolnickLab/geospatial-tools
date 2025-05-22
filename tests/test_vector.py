import geopandas as gpd
import numpy as np
from pandas.testing import assert_frame_equal
from shapely import Polygon

from geospatial_tools.vector import create_vector_grid, spatial_join_within


def test_create_vector_grid_num_of_polygons():
    bbox = [100, 45, 110, 55]
    grid_size = 1
    grid = create_vector_grid(bounding_box=bbox, grid_size=grid_size, crs="EPSG:4326")
    assert len(grid) == 100


def test_create_vector_grid_bounds():
    bbox = [100, 45, 110, 55]
    grid_size = 1
    grid = create_vector_grid(bounding_box=bbox, grid_size=grid_size, crs="EPSG:4326")
    bounds = grid.total_bounds
    bounds = bounds.tolist()
    assert np.array_equal(bbox, bounds), "Arrays are not equal"


def test_spatial_join_within():
    polygon_column = "polygon_id"
    vector_column_name = "joined_polygon_ids"

    polygons = [
        Polygon([(0, 0), (0, 10), (10, 10), (10, 0)]),  # Polygon 1
        Polygon([(10, 0), (10, 10), (20, 10), (20, 0)]),  # Polygon 2
    ]
    polygon_features = gpd.GeoDataFrame({"polygon_id": [1, 2], "geometry": polygons}, crs="EPSG:4326")

    vector_polygons = [
        Polygon([(2, 2), (2, 8), (8, 8), (8, 2)]),  # Completely within Polygon 1
        Polygon([(12, 2), (12, 8), (18, 8), (18, 2)]),  # Completely within Polygon 2
        Polygon([(15, 5), (25, 5), (25, 15), (15, 15)]),  # Partially outside Polygon 2
        Polygon([(30, 30), (30, 40), (40, 40), (40, 30)]),  # Outside any polygon
    ]
    vector_features = gpd.GeoDataFrame(
        {"vector_id": [101, 102, 103, 104], "geometry": vector_polygons}, crs="EPSG:4326"
    )

    result = spatial_join_within(
        polygon_features=polygon_features,
        polygon_column=polygon_column,
        vector_features=vector_features,
        vector_column_name=vector_column_name,
    )

    expected_data = {
        "vector_id": [101, 102, 103, 104],
        "geometry": vector_polygons,
        "joined_polygon_ids": [
            [1],  # Polygon 101 is within Polygon 1
            [2],  # Polygon 102 is within Polygon 2
            [np.nan],  # Polygon 103 is not entirely within any polygon
            [np.nan],  # Polygon 104 is outside any polygon
        ],
    }
    expected_gdf = gpd.GeoDataFrame(expected_data, crs="EPSG:4326")

    result_sorted = result.sort_values("vector_id").reset_index(drop=True)
    expected_sorted = expected_gdf.sort_values("vector_id").reset_index(drop=True)

    assert_frame_equal(
        result_sorted.drop(columns="geometry"),
        expected_sorted.drop(columns="geometry"),
        check_dtype=False,  # Ignore dtype differences if necessary
    )

    for result_geom, expected_geom in zip(result_sorted.geometry, expected_sorted.geometry, strict=False):
        assert result_geom.equals_exact(expected_geom, tolerance=1e-6)
