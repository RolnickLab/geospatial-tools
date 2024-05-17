import numpy as np

from geospatial_tools.vector import create_vector_grid


def test_create_vector_grid_num_of_polygons():
    bbox = [100, 45, 110, 55]
    grid_size = 1
    grid = create_vector_grid(bounding_box=bbox, grid_size=grid_size, crs="EPSG:4326")
    print(grid)
    assert len(grid) == 100


def test_create_vector_grid_bounds():
    bbox = [100, 45, 110, 55]
    grid_size = 1
    grid = create_vector_grid(bounding_box=bbox, grid_size=grid_size, crs="EPSG:4326")
    bounds = grid.total_bounds
    bounds = bounds.tolist()
    assert np.array_equal(bbox, bounds), "Arrays are not equal"
