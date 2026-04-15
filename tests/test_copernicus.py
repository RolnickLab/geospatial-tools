"""
Tests for Copernicus STAC integration and Enums.

This module combines unit tests for Copernicus Enums and integration tests for
the Copernicus STAC catalog.

The integration test:
1. Authenticates with the Copernicus Data Space Ecosystem using credentials from environment variables.
2. Searches for a specific Sentinel-2 tile.
3. Downloads a single band (e.g., B04) to a temporary directory.

Prerequisites for integration test:
- Set COPERNICUS_USERNAME and COPERNICUS_PASSWORD environment variables.
"""

import os

import pytest

from geospatial_tools.copernicus.sentinel_2 import (
    CopernicusS2Band,
    CopernicusS2Collection,
    CopernicusS2Resolution,
)
from geospatial_tools.stac import COPERNICUS, StacSearch
from geospatial_tools.utils import create_logger

LOGGER = create_logger("test_copernicus")


# --- Enum Tests ---


def test_copernicus_s2_collection() -> None:
    """Test CopernicusS2Collection Enum values."""
    assert CopernicusS2Collection.L2A == "sentinel-2-l2a"
    assert CopernicusS2Collection.L1C == "sentinel-2-l1c"


def test_copernicus_s2_resolution() -> None:
    """Test CopernicusS2Resolution Enum values and string representation."""
    assert CopernicusS2Resolution.R10M == 10
    assert CopernicusS2Resolution.R20M == 20
    assert CopernicusS2Resolution.R60M == 60
    assert str(CopernicusS2Resolution.R10M) == "10m"


def test_copernicus_s2_band_native_keys() -> None:
    """Test CopernicusS2Band Enum native resolution keys."""
    # 10m native
    assert CopernicusS2Band.B02 == "B02_10m"
    assert CopernicusS2Band.BLUE == "B02_10m"
    assert CopernicusS2Band.B08 == "B08_10m"
    assert CopernicusS2Band.NIR == "B08_10m"
    assert CopernicusS2Band.TCI == "TCI_10m"

    # 20m native
    assert CopernicusS2Band.B05 == "B05_20m"
    assert CopernicusS2Band.RED_EDGE_1 == "B05_20m"
    assert CopernicusS2Band.B11 == "B11_20m"
    assert CopernicusS2Band.SWIR_1 == "B11_20m"

    # 60m native
    assert CopernicusS2Band.B01 == "B01_60m"
    assert CopernicusS2Band.COASTAL == "B01_60m"
    assert CopernicusS2Band.B09 == "B09_60m"


def test_copernicus_s2_band_explicit_keys() -> None:
    """Test CopernicusS2Band Enum explicit resolution keys."""
    # Verify some explicit resolution members
    assert CopernicusS2Band.B04_10m == "B04_10m"
    assert CopernicusS2Band.B04_20m == "B04_20m"
    assert CopernicusS2Band.B04_60m == "B04_60m"

    assert CopernicusS2Band.B01_20m == "B01_20m"
    assert CopernicusS2Band.B01_60m == "B01_60m"

    assert CopernicusS2Band.SCL_20m == "SCL_20m"
    assert CopernicusS2Band.SCL_60m == "SCL_60m"


def test_copernicus_s2_band_at_res() -> None:
    """Test CopernicusS2Band.at_res() method."""
    # B02 native 10m -> 20m
    assert CopernicusS2Band.B02.at_res(20) == "B02_20m"
    assert CopernicusS2Band.BLUE.at_res(60) == "B02_60m"

    # B05 native 20m -> 60m
    assert CopernicusS2Band.B05.at_res(CopernicusS2Resolution.R60M) == "B05_60m"

    # B01 native 60m -> 20m
    assert CopernicusS2Band.COASTAL.at_res(20) == "B01_20m"


def test_copernicus_s2_band_properties() -> None:
    """Test CopernicusS2Band properties (base_name, native_res)."""
    assert CopernicusS2Band.B02.base_name == "B02"
    assert CopernicusS2Band.BLUE.base_name == "B02"
    assert CopernicusS2Band.B02.native_res == 10

    assert CopernicusS2Band.B01.base_name == "B01"
    assert CopernicusS2Band.B01.native_res == 60

    assert CopernicusS2Band.B05.base_name == "B05"
    assert CopernicusS2Band.B05.native_res == 20


# --- Integration Test ---


@pytest.mark.online
def test_copernicus_integration(tmp_path) -> None:
    """Test the Copernicus STAC integration with S3 download."""
    # Check for credentials
    has_http_creds = os.environ.get("COPERNICUS_USERNAME") and os.environ.get("COPERNICUS_PASSWORD")
    has_s3_creds = os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")

    if not has_http_creds:
        LOGGER.warning("Missing COPERNICUS_USERNAME or COPERNICUS_PASSWORD.")

    if not has_s3_creds:
        LOGGER.warning("Missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY. S3 download might fail if not public.")

    if not has_http_creds and not has_s3_creds:
        pytest.skip("Skipping online test due to missing credentials (HTTP and S3).")

    # Initialize StacSearch with Copernicus catalog
    LOGGER.info("Initializing StacSearch with Copernicus catalog...")
    stac_search = StacSearch(catalog_name=COPERNICUS, logger=LOGGER)

    # Verify S3 client is initialized for Copernicus
    assert stac_search.s3_client is not None, "S3 client should be initialized for Copernicus catalog."

    # Define search parameters
    # Searching for a small area and a specific time range to get a few results
    bbox = (12.4, 41.8, 12.5, 41.9)  # Rome, Italy
    date_range = "2024-06-01/2024-10-30"
    collections = ["sentinel-2-l2a"]

    # Perform search
    LOGGER.info(f"Searching for Sentinel-2 data in {bbox} for {date_range}...")
    results = stac_search.search(
        bbox=bbox,
        date_range=date_range,
        collections=collections,
        max_items=1,  # Limit to 1 item for testing
    )

    if not results:
        pytest.fail("No results found. Search failed.")

    LOGGER.info(f"Found {len(results)} items.")
    item = results[0]
    LOGGER.info(f"First item ID: {item.id}")

    try:
        # Download a single band (e.g., B04 - Red)
        bands = [CopernicusS2Band.B04_10m.value]
        LOGGER.info(f"Downloading band {bands} for item {item.id}...")

        # We use the internal _download_assets method or download_search_results
        # Here we use download_search_results which calls _download_assets
        downloaded_assets = stac_search.download_search_results(bands=bands, base_directory=tmp_path)

        assert downloaded_assets, "Download failed. No assets returned."

        asset = downloaded_assets[0]
        assert list(asset), "Download failed. Asset list is empty."

        downloaded_file = asset[CopernicusS2Band.B04_10m].filename
        assert downloaded_file.exists(), f"File {downloaded_file} does not exist."
        assert downloaded_file.stat().st_size > 0, f"File {downloaded_file} is empty."

        LOGGER.info(f"Successfully downloaded {downloaded_file}")
        LOGGER.info("Copernicus integration test passed!")

    except Exception as e:
        pytest.fail(f"An error occurred during download: {e}")
