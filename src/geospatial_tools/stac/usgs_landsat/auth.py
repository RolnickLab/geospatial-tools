"""Authentication helper for USGS Landsat STAC catalog download."""

import getpass
import logging
import os
import sys
from urllib.parse import urlparse

import requests

from geospatial_tools.utils import create_logger

LOGGER = create_logger(__name__)


def get_usgs_credentials(logger: logging.Logger = LOGGER) -> tuple[str, str]:
    """
    Retrieves USGS EROS credentials from environment variables or prompts the.

    user.

    Args:
        logger: Logger instance.

    Returns:
        A tuple containing the username and token.

    Raises:
        ValueError: If credentials cannot be obtained.
    """
    logger.info("Retrieving USGS EROS credentials...")
    username = os.environ.get("USGS_USERNAME")
    token = os.environ.get("USGS_TOKEN")

    if not username:
        logger.warning("USGS_USERNAME environment variable not set.")
        if sys.stdin.isatty():
            try:
                username = input("Enter your USGS username: ")
            except EOFError as e:
                logger.error("Could not read username from prompt.")
                raise ValueError("USGS_USERNAME environment variable not set and could not prompt user.") from e
        else:
            raise ValueError("USGS_USERNAME environment variable not set in headless environment.")

    if not token:
        logger.warning("USGS_TOKEN environment variable not set.")
        if sys.stdin.isatty():
            try:
                token = getpass.getpass("Enter your USGS EROS M2M token: ")
            except EOFError as e:
                logger.error("Could not read token from prompt.")
                raise ValueError("USGS_TOKEN environment variable not set and could not prompt user.") from e
        else:
            raise ValueError("USGS_TOKEN environment variable not set in headless environment.")

    if not username or not token:
        raise ValueError("Username or token could not be obtained.")

    logger.info("Successfully retrieved USGS EROS credentials.")
    return username, token


def get_usgs_m2m_token(logger: logging.Logger = LOGGER) -> str:
    """
    Requests a session token from the USGS M2M API using USGS credentials.

    Args:
        logger: Logger instance.

    Returns:
        The session token string.

    Raises:
        ValueError: If USGS login response is invalid.
    """
    username, token = get_usgs_credentials(logger)
    login_url = "https://m2m.cr.usgs.gov/api/api/json/stable/login-token"
    data = {"username": username, "token": token}

    try:
        response = requests.post(login_url, json=data, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("text/html"):
            logger.error("Received HTML response from USGS login endpoint.")
            raise ValueError("USGS EROS login returned HTML response instead of JSON.")

        res_json = response.json()
        error_msg = res_json.get("errorMessage")
        if error_msg:
            logger.error(f"USGS login error: {error_msg}")
            raise ValueError(f"USGS EROS login failed: {error_msg}")

        session_token = res_json.get("data")
        if not session_token:
            logger.error("Session token not found in USGS login response.")
            raise ValueError("USGS EROS login response did not contain session token.")

        logger.info("Successfully obtained USGS EROS M2M session token.")
        return session_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to USGS login endpoint: {e}")
        raise


class SessionWithHeaderRedirection(requests.Session):
    """
    Custom session that preserves X-Auth-Token header on redirects to.

    usgs.gov.
    """

    def rebuild_auth(self, prepared_request, response):
        """
        Preserve the X-Auth-Token header when redirecting to another host.

        within usgs.gov.
        """
        token = self.headers.get("X-Auth-Token")
        super().rebuild_auth(prepared_request, response)
        if token:
            parsed_url = urlparse(prepared_request.url)
            hostname = parsed_url.hostname or ""
            if hostname == "usgs.gov" or hostname.endswith(".usgs.gov"):
                prepared_request.headers["X-Auth-Token"] = token
            else:
                prepared_request.headers.pop("X-Auth-Token", None)


def build_usgs_session(logger: logging.Logger = LOGGER) -> requests.Session:
    """
    Builds a requests.Session pre-loaded with the X-Auth-Token header and.

    redirect preservation logic.

    Args:
        logger: Logger instance.

    Returns:
        The customized Session instance.
    """
    session_token = get_usgs_m2m_token(logger)
    session = SessionWithHeaderRedirection()
    session.headers.update({"X-Auth-Token": session_token})
    return session


# Alias for backward/naming compatibility
build_usgs_landsat_session = build_usgs_session
