"""Tests for the STAC module dispatcher logic."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from geospatial_tools.stac.core import (
    CATALOG_NAME_LIST,
    USGS_LANDSAT,
    USGS_LANDSAT_API,
    StacSearch,
    catalog_generator,
    download_stac_asset,
    list_available_catalogs,
)


@pytest.fixture
def mock_s3_client():
    return MagicMock()


@pytest.fixture
def mock_item():
    item = MagicMock()
    item.id = "test_item"
    item.assets = {
        "B02": MagicMock(href="https://eodata.dataspace.copernicus.eu/Sentinel-2/item_B02.tif"),
        "B03": MagicMock(href="https://planetarycomputer.microsoft.com/item_B03.tif"),
    }
    return item


def test_download_stac_asset_http() -> None:
    """Test that download_stac_asset calls download_url for http method."""
    with patch("geospatial_tools.stac.core.download_url") as mock_download_url:
        # Important note : Mocking with patch needs to set path where function is used.
        # This is why, even though 'download_url' comes from stac.copernicus.auth
        # it is still listed here as being from stac.core
        mock_download_url.return_value = Path("test.tif")
        result = download_stac_asset("http://example.com/file.tif", Path("test.tif"), method="http")
        assert result == Path("test.tif")
        mock_download_url.assert_called_once()


def test_download_stac_asset_s3(mock_s3_client) -> None:
    """Test that download_stac_asset calls s3_client.download_file for s3 method."""
    url = "https://eodata.dataspace.copernicus.eu/Sentinel-2/item.tif"
    dest = Path("test.tif")

    # We need to patch utils.parse_s3_url because it's used inside
    with patch("geospatial_tools.stac.utils.parse_s3_url") as mock_parse:
        mock_parse.return_value = ("Sentinel-2", "item.tif")
        result = download_stac_asset(url, dest, method="s3", s3_client=mock_s3_client)

        assert result == dest
        mock_s3_client.download_file.assert_called_once_with("Sentinel-2", "item.tif", str(dest))


def test_stac_search_dispatch_copernicus(mock_item, mock_s3_client) -> None:
    """Test that StacSearch uses s3 for Copernicus."""
    # Important note : Mocking with patch needs to set path where function is used.
    # This is why, even though 'get_copernicus_token' comes from stac.copernicus.auth
    # it is still listed here as being from stac.core
    with (
        patch("geospatial_tools.stac.core.catalog_generator"),
        patch("geospatial_tools.stac.utils.get_s3_client") as mock_get_s3,
        patch("geospatial_tools.stac.core.get_copernicus_token") as mock_get_token,
        patch("geospatial_tools.stac.core.download_stac_asset") as mock_download,
    ):

        mock_get_s3.return_value = mock_s3_client
        mock_get_token.return_value = "fake_token"
        mock_download.return_value = Path("out.tif")

        searcher = StacSearch(catalog_name="copernicus")
        assert searcher.s3_client == mock_s3_client

        searcher._download_assets(mock_item, bands=["B02"], base_directory=Path())

        mock_download.assert_called_once_with(
            asset_url=mock_item.assets["B02"].href,
            destination=Path("test_item_B02.tif"),
            method="s3",
            headers={"Authorization": "Bearer fake_token"},
            s3_client=mock_s3_client,
            logger=searcher.logger,
        )


def test_stac_search_dispatch_other(mock_item) -> None:
    """Test that StacSearch uses http for other catalogs."""
    with (
        patch("geospatial_tools.stac.core.catalog_generator"),
        patch("geospatial_tools.stac.core.download_stac_asset") as mock_download,
    ):

        mock_download.return_value = Path("out.tif")

        searcher = StacSearch(catalog_name="planetary_computer")
        assert searcher.s3_client is None

        searcher._download_assets(mock_item, bands=["B03"], base_directory=Path())

        mock_download.assert_called_once_with(
            asset_url=mock_item.assets["B03"].href,
            destination=Path("test_item_B03.tif"),
            method="http",
            headers=None,
            s3_client=None,
            logger=searcher.logger,
        )


def test_list_available_catalogs_usgs_landsat():
    """Test that USGS_LANDSAT is in the available catalogs list."""
    catalogs = list_available_catalogs()
    assert USGS_LANDSAT in catalogs
    assert USGS_LANDSAT in CATALOG_NAME_LIST


def test_catalog_generator_usgs_landsat():
    """Test that catalog_generator(USGS_LANDSAT) returns a client."""
    mock_client = MagicMock()
    with patch("pystac_client.Client.open", return_value=mock_client) as mock_open:
        client = catalog_generator(USGS_LANDSAT)
        assert client == mock_client
        mock_open.assert_called_once_with(USGS_LANDSAT_API)


def test_create_usgs_landsat_catalog_retry():
    """Test retry behavior for create_usgs_landsat_catalog."""
    from geospatial_tools.stac.core import create_usgs_landsat_catalog

    mock_client = MagicMock()
    call_count = 0

    def mock_open(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Connection failed")
        return mock_client

    with (
        patch("pystac_client.Client.open", side_effect=mock_open),
        patch("time.sleep") as mock_sleep,
    ):
        client = create_usgs_landsat_catalog(max_retries=3, delay=1)
        assert client == mock_client
        assert call_count == 3
        assert mock_sleep.call_count == 2
