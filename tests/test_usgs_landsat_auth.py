"""
Unit tests for USGS Landsat authentication, credentials gathering, and safe.

downloading.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from geospatial_tools.stac.usgs_landsat.auth import (
    SessionWithHeaderRedirection,
    get_usgs_credentials,
    get_usgs_m2m_token,
)
from geospatial_tools.utils import download_url


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock()


# ---------------------------------------------------------------------------
# 6.5.1: get_usgs_credentials - Headless and TTY missing credentials
# ---------------------------------------------------------------------------


def test_get_usgs_credentials_from_env(mock_logger) -> None:
    """Verify credentials resolved from environment variables."""
    env = {"USGS_USERNAME": "test_user", "USGS_TOKEN": "test_token_123"}
    with patch.dict("os.environ", env):
        username, token = get_usgs_credentials(mock_logger)
        assert username == "test_user"
        assert token == "test_token_123"


def test_get_usgs_credentials_headless_missing_username(mock_logger) -> None:
    """Verify ValueError is raised if username is missing in headless environment."""
    env = {"USGS_TOKEN": "test_token_123"}
    with patch.dict("os.environ", env):
        with patch("sys.stdin.isatty", return_value=False):
            with pytest.raises(ValueError, match="USGS_USERNAME environment variable not set"):
                get_usgs_credentials(mock_logger)


def test_get_usgs_credentials_headless_missing_token(mock_logger) -> None:
    """Verify ValueError is raised if token is missing in headless environment."""
    env = {"USGS_USERNAME": "test_user"}
    with patch.dict("os.environ", env):
        with patch("sys.stdin.isatty", return_value=False):
            with pytest.raises(ValueError, match="USGS_TOKEN environment variable not set"):
                get_usgs_credentials(mock_logger)


def test_get_usgs_credentials_tty_missing_username(mock_logger) -> None:
    """Verify user is prompted for username if missing in a TTY environment."""
    env = {"USGS_TOKEN": "test_token_123"}
    with patch.dict("os.environ", env):
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("builtins.input", return_value="prompted_user") as mock_input,
        ):
            username, token = get_usgs_credentials(mock_logger)
            assert username == "prompted_user"
            assert token == "test_token_123"
            mock_input.assert_called_once_with("Enter your USGS username: ")


def test_get_usgs_credentials_tty_missing_token(mock_logger) -> None:
    """Verify user is prompted for token if missing in a TTY environment."""
    env = {"USGS_USERNAME": "test_user"}
    with patch.dict("os.environ", env):
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("getpass.getpass", return_value="prompted_token") as mock_getpass,
        ):
            username, token = get_usgs_credentials(mock_logger)
            assert username == "test_user"
            assert token == "prompted_token"
            mock_getpass.assert_called_once_with("Enter your USGS EROS M2M token: ")


# ---------------------------------------------------------------------------
# 6.5.2: get_usgs_m2m_token - Successful/Failed USGS EROS login
# ---------------------------------------------------------------------------


def test_get_usgs_m2m_token_success(mock_logger) -> None:
    """Verify EROS login returns session token string on success."""
    env = {"USGS_USERNAME": "test_user", "USGS_TOKEN": "test_token"}
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"errorMessage": None, "data": "session_api_key_456"}

    with (
        patch.dict("os.environ", env),
        patch("requests.post", return_value=mock_response) as mock_post,
    ):
        session_token = get_usgs_m2m_token(mock_logger)
        assert session_token == "session_api_key_456"
        mock_post.assert_called_once_with(
            "https://m2m.cr.usgs.gov/api/api/json/stable/login-token",
            json={"username": "test_user", "token": "test_token"},
            timeout=30,
        )


def test_get_usgs_m2m_token_html_response(mock_logger) -> None:
    """Verify ValueError is raised if EROS login endpoint returns HTML."""
    env = {"USGS_USERNAME": "test_user", "USGS_TOKEN": "test_token"}
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "text/html"}

    with (
        patch.dict("os.environ", env),
        patch("requests.post", return_value=mock_response),
    ):
        with pytest.raises(ValueError, match="USGS EROS login returned HTML response"):
            get_usgs_m2m_token(mock_logger)


def test_get_usgs_m2m_token_api_error(mock_logger) -> None:
    """Verify ValueError is raised if EROS response contains errorMessage."""
    env = {"USGS_USERNAME": "test_user", "USGS_TOKEN": "test_token"}
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"errorMessage": "Invalid application token", "data": None}

    with (
        patch.dict("os.environ", env),
        patch("requests.post", return_value=mock_response),
    ):
        with pytest.raises(ValueError, match="USGS EROS login failed: Invalid application token"):
            get_usgs_m2m_token(mock_logger)


# ---------------------------------------------------------------------------
# 6.5.3: SessionWithHeaderRedirection.rebuild_auth
# ---------------------------------------------------------------------------


def test_session_rebuild_auth_preserves_usgs_redirect() -> None:
    """
    Verify X-Auth-Token preserved on USGS.gov redirects but removed on other.

    domains.
    """
    session = SessionWithHeaderRedirection()
    session.headers.update({"X-Auth-Token": "secret_token"})

    # Prepare mocked request/response for usgs redirect
    req_usgs = MagicMock()
    req_usgs.url = "https://landsatlook.usgs.gov/data/123"
    req_usgs.headers = {}
    resp_usgs = MagicMock()

    session.rebuild_auth(req_usgs, resp_usgs)
    assert req_usgs.headers["X-Auth-Token"] == "secret_token"

    # Prepare mocked request/response for non-usgs redirect
    req_other = MagicMock()
    req_other.url = "https://some-unrelated-domain.com/file"
    req_other.headers = {"X-Auth-Token": "secret_token"}
    resp_other = MagicMock()

    session.rebuild_auth(req_other, resp_other)
    assert "X-Auth-Token" not in req_other.headers


# ---------------------------------------------------------------------------
# 6.5.4: download_url Refactor - HTML rejection, streaming, atomic-rename
# ---------------------------------------------------------------------------


def test_download_url_rejects_html(tmp_path, mock_logger) -> None:
    """
    Verify download_url raises ValueError on text/html Content-Type without.

    saving files.
    """
    dest_file = tmp_path / "asset.tif"
    partial_file = tmp_path / "asset.tif.partial"

    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "text/html"}

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Rejection: Content-Type is text/html"):
            download_url(url="http://example.com/asset.tif", filename=dest_file, logger=mock_logger)

    assert not dest_file.exists()
    assert not partial_file.exists()


def test_download_url_atomic_streaming(tmp_path, mock_logger) -> None:
    """
    Verify download_url streams content to .partial and renames it on.

    completion.
    """
    dest_file = tmp_path / "asset.tif"
    partial_file = tmp_path / "asset.tif.partial"

    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "image/tiff"}
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]

    with patch("requests.get", return_value=mock_response) as mock_get:
        download_url(url="http://example.com/asset.tif", filename=dest_file, logger=mock_logger)
        mock_get.assert_called_once_with(
            "http://example.com/asset.tif", headers=None, stream=True, timeout=60, allow_redirects=True
        )

    assert dest_file.exists()
    assert dest_file.read_bytes() == b"chunk1chunk2"
    assert not partial_file.exists()


def test_download_url_failure_cleanup(tmp_path, mock_logger) -> None:
    """Verify download_url cleans up .partial file on download exception."""
    dest_file = tmp_path / "asset.tif"
    partial_file = tmp_path / "asset.tif.partial"

    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "image/tiff"}

    def raising_generator(*args, **kwargs):
        yield b"chunk1"
        raise requests.exceptions.ChunkedEncodingError("Connection lost mid-stream")

    mock_response.iter_content.side_effect = raising_generator

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.ChunkedEncodingError):
            download_url(url="http://example.com/asset.tif", filename=dest_file, logger=mock_logger)

    assert not dest_file.exists()
    assert not partial_file.exists()
