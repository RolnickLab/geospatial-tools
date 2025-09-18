import pytest

from geospatial_tools.download import download_s2_tiling_grid, download_usa_polygon


@pytest.mark.skip(reason="Currently a problem with SSL certificate of host census.gov")
def test_download_1usa_polygon(tmp_path):
    """
    If this test fails, it is usually because the domain has problems with it's ssl certificate.

    The data can usually still be downloaded manually through a browser.
    """
    file_list = download_usa_polygon(output_directory=tmp_path)
    assert len(file_list) == 7


def test_download_s2_tilling_grid(tmp_path):
    file_list = download_s2_tiling_grid(output_directory=tmp_path)
    assert len(file_list) == 1
