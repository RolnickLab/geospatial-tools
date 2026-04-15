"""This module contains authentication-related functions."""

import getpass
import logging
import os

import requests

from geospatial_tools.utils import create_logger

LOGGER = create_logger(__name__)

COPERNICUS_AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


def get_copernicus_credentials(logger: logging.Logger = LOGGER) -> tuple[str, str] | None:
    """
    Retrieves Copernicus credentials from environment variables or prompts the user.

    This function first checks for `COPERNICUS_USERNAME` and `COPERNICUS_PASSWORD`
    environment variables. If they are not set, it interactively prompts the user
    for their username and password.

    Using environment variables is recommended for security and to comply with the
    12-factor app methodology, which separates configuration from code. This prevents
    hardcoding sensitive information and makes the application more portable across
    different environments (development, testing, production).

    Args:
        logger: Logger instance.

    Returns:
        A tuple containing the username and password, or None if they could not be
        obtained.
    """
    logger.info("Retrieving Copernicus credentials...")
    username = os.environ.get("COPERNICUS_USERNAME")
    password = os.environ.get("COPERNICUS_PASSWORD")

    if not username:
        logger.warning("COPERNICUS_USERNAME environment variable not set.")
        try:
            username = input("Enter your Copernicus username: ")
        except EOFError:
            logger.error("Could not read username from prompt.")
            return None

    if not password:
        logger.warning("COPERNICUS_PASSWORD environment variable not set.")
        try:
            password = getpass.getpass("Enter your Copernicus password: ")
        except EOFError:
            logger.error("Could not read password from prompt.")
            return None

    if not username or not password:
        logger.error("Username or password could not be obtained. Cannot proceed with authentication.")
        return None

    logger.info("Successfully retrieved Copernicus credentials.")
    return username, password


def get_copernicus_token(logger: logging.Logger = LOGGER) -> str | None:
    """
    Retrieves an access token from the Copernicus Data Space Ecosystem.

    This function uses the credentials obtained from `get_copernicus_credentials`
    to request an access token from the authentication endpoint.

    Args:
        logger: Logger instance.

    Returns:
        The access token as a string, or None if authentication fails.
    """
    credentials = get_copernicus_credentials(logger)
    if not credentials:
        return None

    username, password = credentials
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    try:
        response = requests.post(COPERNICUS_AUTH_URL, data=data, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        if access_token:
            logger.info("Successfully obtained Copernicus access token.")
            return access_token
        logger.error("Access token not found in response.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to obtain access token: {e}")
        return None
