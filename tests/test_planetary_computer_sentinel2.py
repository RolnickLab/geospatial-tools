import pytest

from geospatial_tools.stac.planetary_computer.sentinel_2 import Sentinel2Search


@pytest.mark.integration
def test_sentinel2_search_integration():
    """Integration test for Sentinel-2 search on Planetary Computer."""
    searcher = Sentinel2Search(date_range="2023-06-01/2023-06-30", bbox=(-74.0, 45.4, -73.5, 45.7))
    searcher.filter_by_cloud_cover(10).filter_by_nodata_pixel_percentage(5)

    results = searcher.search()

    assert results is not None
    assert len(results) > 0
    for item in results:
        assert item.properties["eo:cloud_cover"] < 10
        assert item.properties["s2:nodata_pixel_percentage"] < 5


@pytest.mark.integration
def test_sentinel2_search_mgrs_integration():
    """Integration test for Sentinel-2 search using MGRS tile."""
    searcher = Sentinel2Search(date_range="2023-06-01/2023-06-07")
    searcher.filter_by_mgrs_tile("31UFS")

    results = searcher.search()

    assert results is not None
    assert len(results) > 0
    for item in results:
        assert item.properties["s2:mgrs_tile"] == "31UFS"
