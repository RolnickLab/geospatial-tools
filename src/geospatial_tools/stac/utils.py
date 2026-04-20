from __future__ import annotations

import calendar
import datetime
import os
from urllib.parse import urlparse

import boto3

from geospatial_tools.utils import create_logger


def create_date_range_for_specific_period(
    start_year: int, end_year: int, start_month_range: int, end_month_range: int
) -> list[str]:
    """
    This function create a list of date ranges.

    For example, I want to create date ranges for 2020 and 2021, but only for the months from March to May.
    I therefore expect to have 2 ranges: [2020-03-01 to 2020-05-30, 2021-03-01 to 2021-05-30].

    Handles the automatic definition of the last day for the end month, as well as periods that cross over years

    For example, I want to create date ranges for 2020 and 2022, but only for the months from November to January.
    I therefore expect to have 2 ranges: [2020-11-01 to 2021-01-31, 2021-11-01 to 2022-01-31].

    Args:
      start_year: Start year for ranges
      end_year: End year for ranges
      start_month_range: Starting month for each period
      end_month_range: End month for each period (inclusively)

    Returns:
    """
    date_ranges = []
    year_bump = 0
    if start_month_range > end_month_range:
        year_bump = 1
    range_end_year = end_year + 1 - year_bump
    for year in range(start_year, range_end_year):
        start_date = datetime.datetime(year, start_month_range, 1)
        last_day = calendar.monthrange(year + year_bump, end_month_range)[1]
        end_date = datetime.datetime(year + year_bump, end_month_range, last_day, 23, 59, 59)
        date_ranges.append(f"{start_date.isoformat()}Z/{end_date.isoformat()}Z")
    return date_ranges


LOGGER = create_logger(__name__)


def get_s3_client(endpoint_url: str | None = None) -> boto3.client:
    """
    Creates and returns a boto3 S3 client.

    Args:
        endpoint_url: The S3 endpoint URL. If None, it attempts to use
                      the COPERNICUS_S3_ENDPOINT environment variable.

    Returns:
        A boto3 S3 client.
    """
    if not endpoint_url:
        endpoint_url = os.environ.get("COPERNICUS_S3_ENDPOINT", "https://eodata.dataspace.copernicus.eu")

    access_key = os.environ.get("AWS_ACCESS_KEY_ID") or None
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY") or None

    if not access_key or not secret_key:
        LOGGER.warning("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not found in environment.")

    LOGGER.info(f"Creating S3 client with endpoint: [{endpoint_url}]")

    # Note: boto3 automatically picks up AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    # from the environment, but we can also pass them explicitly if needed.
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def parse_s3_url(url: str) -> tuple[str, str]:
    """
    Parses an S3 URL or a CDSE STAC href to extract the bucket and key.

    Expected formats:
    - s3://bucket/key
    - https://eodata.dataspace.copernicus.eu/bucket/key
    - https://zipper.dataspace.copernicus.eu/download/uuid (this might not be a direct S3 key)

    Args:
        url: The URL to parse.

    Returns:
        A tuple of (bucket, key).

    Raises:
        ValueError: If the URL cannot be parsed into a bucket and key.
    """
    parsed = urlparse(url)

    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        return bucket, key

    if parsed.scheme in ["http", "https"]:
        # For CDSE eodata endpoint, the path starts with the bucket
        # e.g., /Sentinel-2/MSI/L2A/2023/01/01/...
        path_parts = parsed.path.lstrip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError(f"URL path does not contain enough parts to determine bucket and key: {url}")

        bucket = path_parts[0]
        key = "/".join(path_parts[1:])
        return bucket, key

    raise ValueError(f"Unsupported URL scheme: {parsed.scheme} in URL: {url}")


def download_url_s3(
    asset_url,
    destination,
    logger,
    s3_client,
):
    if not s3_client:
        s3_client = get_s3_client()
    try:
        bucket, key = parse_s3_url(asset_url)
        logger.info(f"Downloading from S3: bucket=[{bucket}], key=[{key}] to [{destination}]")
        s3_client.download_file(bucket, key, str(destination))
        return destination
    except Exception as e:  # pylint: disable=W0718
        logger.error(f"S3 download failed for {asset_url}: {e}")
        return None
