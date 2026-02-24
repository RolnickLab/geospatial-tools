"""
Manual test script for Copernicus STAC integration.

This script verifies that the Copernicus STAC catalog integration works as expected.
It performs the following steps:
1. Authenticates with the Copernicus Data Space Ecosystem using credentials from environment variables.
2. Searches for a specific Sentinel-2 tile.
3. Downloads a single band (e.g., B04) to a temporary directory.

Prerequisites:
- Set COPERNICUS_USERNAME and COPERNICUS_PASSWORD environment variables.
"""

import os
import shutil
from pathlib import Path

from geospatial_tools.stac import COPERNICUS, StacSearch
from geospatial_tools.utils import create_logger

LOGGER = create_logger("manual_copernicus_test")


def test_copernicus_integration():
    """Test the Copernicus STAC integration."""
    # Check for credentials
    if not os.environ.get("COPERNICUS_USERNAME") or not os.environ.get("COPERNICUS_PASSWORD"):
        LOGGER.error(
            "Please set COPERNICUS_USERNAME and COPERNICUS_PASSWORD environment variables before running this test."
        )
        return

    # Initialize StacSearch with Copernicus catalog
    LOGGER.info("Initializing StacSearch with Copernicus catalog...")
    stac_search = StacSearch(catalog_name=COPERNICUS, logger=LOGGER)

    # Define search parameters
    # Searching for a small area and a specific time range to get a few results
    bbox = [12.4, 41.8, 12.5, 41.9]  # Rome, Italy
    date_range = "2025-06-01/2025-10-30"
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
        LOGGER.error("No results found. Search failed.")
        return

    LOGGER.info(f"Found {len(results)} items.")
    item = results[0]
    LOGGER.info(f"First item ID: {item.id}")

    # Create a temporary directory for download
    download_dir = Path("temp_copernicus_download")
    if download_dir.exists():
        shutil.rmtree(download_dir)
    download_dir.mkdir()

    try:
        # Download a single band (e.g., B04 - Red)
        bands = ["B04"]
        LOGGER.info(f"Downloading band {bands} for item {item.id}...")

        # We use the internal _download_assets method or download_search_results
        # Here we use download_search_results which calls _download_assets
        downloaded_assets = stac_search.download_search_results(bands=bands, base_directory=download_dir)

        if not downloaded_assets:
            LOGGER.error("Download failed. No assets returned.")
            return

        asset = downloaded_assets[0]
        if not asset.list:
            LOGGER.error("Download failed. Asset list is empty.")
            return

        downloaded_file = asset.list[0].filename
        if downloaded_file.exists() and downloaded_file.stat().st_size > 0:
            LOGGER.info(f"Successfully downloaded {downloaded_file}")
            LOGGER.info("Copernicus integration test passed!")
        else:
            LOGGER.error(f"File {downloaded_file} does not exist or is empty.")

    except Exception as e:
        LOGGER.error(f"An error occurred during download: {e}")
    finally:
        # Cleanup
        if download_dir.exists():
            LOGGER.info("Cleaning up temporary directory...")
            shutil.rmtree(download_dir)


if __name__ == "__main__":
    test_copernicus_integration()
