"""Utility module for S3 operations related to Copernicus Data Space Ecosystem."""

import os
from urllib.parse import urlparse

import boto3

from geospatial_tools.utils import create_logger

# Initialize logger
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


if __name__ == "__main__":
    # Simple manual test
    test_url = "s3://Sentinel-2/MSI/L2A/2023/01/01/S2B_MSIL2A_20230101T103039_N0509_R108_T32TQM_20230101T123225.SAFE"
    b, k = parse_s3_url(test_url)
    print(f"Bucket: {b}, Key: {k}")

    test_https_url = "https://eodata.dataspace.copernicus.eu/Sentinel-2/MSI/L2A/2023/01/01/S2B_MSIL2A_20230101T103039_N0509_R108_T32TQM_20230101T123225.SAFE"
    b, k = parse_s3_url(test_https_url)
    print(f"Bucket: {b}, Key: {k}")
