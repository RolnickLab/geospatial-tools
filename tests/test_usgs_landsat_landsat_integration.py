"""Integration tests for live Landsat 8 & 9 searches against the USGS_EROS STAC server."""

import datetime

import pytest

from geospatial_tools.stac.usgs_landsat import Landsat8Search, Landsat9Search
from geospatial_tools.stac.usgs_landsat.constants import (
    UsgsLandsatLandsatBand,
    UsgsLandsatLandsatCollection,
)


@pytest.mark.integration
def test_landsat8_search_returns_items_from_cmr_usgs_eros() -> None:
    """Verify Landsat 8 search returns valid items and correct asset structures from live STAC server."""
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=120)
    end_date = today - datetime.timedelta(days=3)
    date_range = f"{start_date.isoformat()}/{end_date.isoformat()}"

    # Bounding box covering Seattle, WA area
    bbox = (-122.5, 47.5, -122.0, 48.0)

    searcher = Landsat8Search(date_range=date_range, bbox=bbox)
    results = searcher.search()

    assert results is not None
    assert len(results) > 0

    expected_bands = {
        UsgsLandsatLandsatBand.COASTAL,
        UsgsLandsatLandsatBand.BLUE,
        UsgsLandsatLandsatBand.GREEN,
        UsgsLandsatLandsatBand.RED,
        UsgsLandsatLandsatBand.NIR08,
        UsgsLandsatLandsatBand.SWIR16,
        UsgsLandsatLandsatBand.SWIR22,
        UsgsLandsatLandsatBand.PAN,
        UsgsLandsatLandsatBand.CIRRUS,
        UsgsLandsatLandsatBand.LWIR11,
        UsgsLandsatLandsatBand.LWIR12,
        UsgsLandsatLandsatBand.QA_PIXEL,
        UsgsLandsatLandsatBand.QA_RADSAT,
        UsgsLandsatLandsatBand.SAA,
        UsgsLandsatLandsatBand.SZA,
        UsgsLandsatLandsatBand.VAA,
        UsgsLandsatLandsatBand.VZA,
        UsgsLandsatLandsatBand.ANG_TXT,
        UsgsLandsatLandsatBand.MTL_JSON,
        UsgsLandsatLandsatBand.MTL_TXT,
        UsgsLandsatLandsatBand.MTL_XML,
        UsgsLandsatLandsatBand.THUMBNAIL,
        UsgsLandsatLandsatBand.REDUCED_RESOLUTION_BROWSE,
        UsgsLandsatLandsatBand.INDEX,
    }

    for item in results:
        assert item.properties["platform"] == "LANDSAT_8"
        assert item.collection_id == UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2.value

        # Verify every expected band is present in the item's assets dict
        for band in expected_bands:
            assert band.value in item.assets


@pytest.mark.integration
def test_landsat9_search_returns_items_from_cmr_usgs_eros() -> None:
    """Verify Landsat 9 search returns valid items and correct asset structures from live STAC server."""
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=120)
    end_date = today - datetime.timedelta(days=3)
    date_range = f"{start_date.isoformat()}/{end_date.isoformat()}"

    # Bounding box covering Seattle, WA area
    bbox = (-122.5, 47.5, -122.0, 48.0)

    searcher = Landsat9Search(date_range=date_range, bbox=bbox)
    results = searcher.search()

    assert results is not None
    assert len(results) > 0

    expected_bands = {
        UsgsLandsatLandsatBand.COASTAL,
        UsgsLandsatLandsatBand.BLUE,
        UsgsLandsatLandsatBand.GREEN,
        UsgsLandsatLandsatBand.RED,
        UsgsLandsatLandsatBand.NIR08,
        UsgsLandsatLandsatBand.SWIR16,
        UsgsLandsatLandsatBand.SWIR22,
        UsgsLandsatLandsatBand.PAN,
        UsgsLandsatLandsatBand.CIRRUS,
        UsgsLandsatLandsatBand.LWIR11,
        UsgsLandsatLandsatBand.LWIR12,
        UsgsLandsatLandsatBand.QA_PIXEL,
        UsgsLandsatLandsatBand.QA_RADSAT,
        UsgsLandsatLandsatBand.SAA,
        UsgsLandsatLandsatBand.SZA,
        UsgsLandsatLandsatBand.VAA,
        UsgsLandsatLandsatBand.VZA,
        UsgsLandsatLandsatBand.ANG_TXT,
        UsgsLandsatLandsatBand.MTL_JSON,
        UsgsLandsatLandsatBand.MTL_TXT,
        UsgsLandsatLandsatBand.MTL_XML,
        UsgsLandsatLandsatBand.THUMBNAIL,
        UsgsLandsatLandsatBand.REDUCED_RESOLUTION_BROWSE,
        UsgsLandsatLandsatBand.INDEX,
    }

    for item in results:
        assert item.properties["platform"] == "LANDSAT_9"
        assert item.collection_id == UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2.value

        # Verify every expected band is present in the item's assets dict
        for band in expected_bands:
            assert band.value in item.assets
