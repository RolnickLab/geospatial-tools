"""Tests for the S3 utility module."""

import os
from unittest.mock import patch

import pytest

from geospatial_tools.s3_utils import get_s3_client, parse_s3_url


def test_parse_s3_url_valid_s3_scheme() -> None:
    """Test parsing a valid s3:// URL."""
    url = "s3://sentinel-2/MSI/L2A/2023/01/01/item.SAFE"
    bucket, key = parse_s3_url(url)
    assert bucket == "sentinel-2"
    assert key == "MSI/L2A/2023/01/01/item.SAFE"


def test_parse_s3_url_valid_https_scheme() -> None:
    """Test parsing a valid https:// URL representing an S3 path."""
    url = "https://eodata.dataspace.copernicus.eu/Sentinel-2/MSI/L2A/2023/01/01/item.SAFE"
    bucket, key = parse_s3_url(url)
    assert bucket == "Sentinel-2"
    assert key == "MSI/L2A/2023/01/01/item.SAFE"


def test_parse_s3_url_invalid_scheme() -> None:
    """Test parsing a URL with an unsupported scheme."""
    url = "ftp://eodata.dataspace.copernicus.eu/bucket/key"
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        parse_s3_url(url)


def test_parse_s3_url_no_path() -> None:
    """Test parsing a URL with no path after the bucket."""
    url = "https://eodata.dataspace.copernicus.eu/bucket"
    with pytest.raises(ValueError, match="URL path does not contain enough parts"):
        parse_s3_url(url)


@patch("boto3.client")
def test_get_s3_client_custom_endpoint(mock_boto_client) -> None:
    """Test creating an S3 client with a custom endpoint."""
    endpoint = "https://my-custom-endpoint.com"
    with patch.dict(os.environ, {}, clear=True):
        get_s3_client(endpoint_url=endpoint)
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    )


@patch("boto3.client")
def test_get_s3_client_env_endpoint(mock_boto_client) -> None:
    """Test creating an S3 client using the endpoint from environment variable."""
    endpoint = "https://env-endpoint.com"
    with patch.dict(os.environ, {"COPERNICUS_S3_ENDPOINT": endpoint}, clear=True):
        get_s3_client()
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    )


@patch("boto3.client")
def test_get_s3_client_with_credentials(mock_boto_client) -> None:
    """Test creating an S3 client with credentials from environment."""
    endpoint = "https://eodata.dataspace.copernicus.eu"
    env_vars = {
        "AWS_ACCESS_KEY_ID": "my_access_key",
        "AWS_SECRET_ACCESS_KEY": "my_secret_key",
        "COPERNICUS_S3_ENDPOINT": endpoint,
    }
    with patch.dict(os.environ, env_vars, clear=True):
        get_s3_client()
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id="my_access_key",
        aws_secret_access_key="my_secret_key",
    )
