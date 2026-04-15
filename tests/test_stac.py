"""Tests for the STAC module dispatcher logic."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from geospatial_tools.stac import StacSearch, download_stac_asset


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
    with patch("geospatial_tools.stac.download_url") as mock_download_url:
        mock_download_url.return_value = Path("test.tif")
        result = download_stac_asset("http://example.com/file.tif", Path("test.tif"), method="http")
        assert result == Path("test.tif")
        mock_download_url.assert_called_once()


def test_download_stac_asset_s3(mock_s3_client) -> None:
    """Test that download_stac_asset calls s3_client.download_file for s3 method."""
    url = "https://eodata.dataspace.copernicus.eu/Sentinel-2/item.tif"
    dest = Path("test.tif")

    # We need to patch s3_utils.parse_s3_url because it's used inside
    with patch("geospatial_tools.s3_utils.parse_s3_url") as mock_parse:
        mock_parse.return_value = ("Sentinel-2", "item.tif")
        result = download_stac_asset(url, dest, method="s3", s3_client=mock_s3_client)

        assert result == dest
        mock_s3_client.download_file.assert_called_once_with("Sentinel-2", "item.tif", str(dest))


def test_stac_search_dispatch_copernicus(mock_item, mock_s3_client) -> None:
    """Test that StacSearch uses s3 for Copernicus."""
    with (
        patch("geospatial_tools.stac.catalog_generator"),
        patch("geospatial_tools.s3_utils.get_s3_client") as mock_get_s3,
        patch("geospatial_tools.stac.get_copernicus_token") as mock_get_token,
        patch("geospatial_tools.stac.download_stac_asset") as mock_download,
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
        patch("geospatial_tools.stac.catalog_generator"),
        patch("geospatial_tools.stac.download_stac_asset") as mock_download,
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
