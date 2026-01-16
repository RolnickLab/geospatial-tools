"""This module contains general utility functions."""

from __future__ import annotations

import calendar
import datetime
import json
import logging
import os
import struct
import sys
import zipfile
from pathlib import Path
from typing import Any, Optional

import requests
import yaml
from rasterio import CRS

from geospatial_tools import CONFIGS

GEOPACKAGE_DRIVER = "GPKG"

# GZIP header positions
FTEXT = 0x01
FHCRC = 0x02
FEXTRA = 0x04
FNAME = 0x08
FCOMMENT = 0x10


def create_logger(logger_name: str) -> logging.Logger:
    """
    Creates a logger object using input name parameter that outputs to stdout.

    Args:
      logger_name: Name of logger

    Returns:
    """
    logging_level = logging.INFO
    app_config_path = CONFIGS / "geospatial_tools_ini.yaml"
    if app_config_path.exists():
        with app_config_path.open("r", encoding="UTF-8") as config_file:
            application_params = yaml.safe_load(config_file)
            logger_params = application_params["logging"]
            logging_level = logger_params["logging_level"].upper()
    if os.getenv("GEO_LOG_LEVEL"):
        logging_level = os.getenv("GEO_LOG_LEVEL").upper()

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-10.10s [%(threadName)s][%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOGGER = create_logger(__name__)


def get_yaml_config(yaml_config_file: str, logger: logging.Logger = LOGGER) -> dict:
    """
    This function takes in the path, or name of the file if it can be found in the config/ folder, with of without the
    extension, and returns the values of the file in a dictionary format.

    Ex. For a file named app_config.yml (or app_config.yaml), directly in the config/ folder,
        the function could be called like so : `params = get_yaml_config('app_config')`

    Args:
      yaml_config_file: Path to yaml config file. If config file is in the config folder,
        you can use the file's name without the extension.
      logger: Logger to handle messaging, by default LOGGER

    Returns:
    """

    potential_paths = [
        Path(yaml_config_file),
        CONFIGS / yaml_config_file,
        CONFIGS / f"{yaml_config_file}.yaml",
        CONFIGS / f"{yaml_config_file}.yml",
    ]

    config_filepath = None
    for path in potential_paths:
        if path.exists():
            config_filepath = path
            logger.info(f"Yaml config file [{path!s}] found.")
            break

    params = {}
    if not config_filepath:
        logger.error(f"Yaml config file [{yaml_config_file}] was not found.")
        return params

    try:
        with config_filepath.open("r", encoding="UTF-8") as file:
            logger.info(f"Loading YAML config file [{config_filepath}].")
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.warning(f"Error loading YAML file [{config_filepath}]: {e}")
        return {}


def get_json_config(json_config_file: str, logger=LOGGER) -> dict:
    """
    This function takes in the path, or name of the file if it can be found in the config/ folder, with of without the
    extension, and returns the values of the file in a dictionary format.

    Ex. For a file named app_config.json, directly in the config/ folder,
        the function could be called like so : `params = get_json_config('app_config')`

    Args:
      json_config_file: Path to JSON config file. If config file is in the config folder,
      logger: Logger to handle messaging

    Returns:
    """

    potential_paths = [
        Path(json_config_file),
        CONFIGS / json_config_file,
        CONFIGS / f"{json_config_file}.json",
    ]

    config_filepath = None
    for path in potential_paths:
        if path.exists():
            config_filepath = path
            logger.info(f"JSON config file [{path!s}] found.")
            break

    if not config_filepath:
        logger.error(f"JSON config file [{json_config_file}] not found.")
        return {}

    try:
        with config_filepath.open("r", encoding="UTF-8") as file:
            logger.info(f"Loading JSON config file [{config_filepath}].")
            return json.load(file)
    except json.JSONDecodeError as e:
        logger.warning(f"Error loading JSON file [{config_filepath}]: {e}")
        return {}


def create_crs(dataset_crs: str | int, logger=LOGGER):
    """

    Args:
      dataset_crs: EPSG code in string or int format. Can be given in the following ways: 5070 | "5070" | "EPSG:5070"
      logger: Logger instance (Default value = LOGGER)

    Returns:


    """
    logger.info(f"Creating EPSG code from following input : [{dataset_crs}]")
    is_int = isinstance(dataset_crs, int) or dataset_crs.isnumeric()
    is_str = isinstance(dataset_crs, str)
    contains_epsg = is_str and "EPSG:" in dataset_crs
    if is_int:
        return CRS.from_epsg(dataset_crs)
    if contains_epsg:
        return CRS.from_string(dataset_crs.upper())
    if ":" in dataset_crs:
        logger.warning("Input is not conform to standards. Attempting to extract code from the provided input.")
        recovered_code = dataset_crs.split(":")[-1]
        if recovered_code.isnumeric():
            return CRS.from_epsg(recovered_code)

    logger.error(f"Encountered problem while trying to format EPSG code from input : [{dataset_crs}]")
    return None


def download_url(url: str, filename: str | Path, overwrite: bool = False, logger=LOGGER) -> Path | None:
    """
    This function downloads a file from a given URL.

    Args:
      url: Url to download
      filename: Filename (or full path) to save the downloaded file
      overwrite: If True, overwrite existing file
      logger: Logger instance

    Returns:
    """
    if isinstance(filename, str):
        filename = Path(filename)

    if filename.exists() and not overwrite:
        logger.info(f"File [{filename}] already exists. Skipping download.")
        return filename

    response = requests.get(url, timeout=None)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        logger.info(f"Downloaded {filename} successfully.")
        return filename

    logger.error(f"Failed to download the asset. Status code: {response.status_code}")
    return None


def unzip_file(zip_path: str | Path, extract_to: str | Path, logger: logging.Logger = LOGGER) -> list[str | Path]:
    """
    This function unzips an archive to a specific directory.

    Args:
      zip_path: Path to zip file
      extract_to: Path of directory to extract the zip file
      logger: Logger instance

    Returns:
    """
    if isinstance(zip_path, str):
        zip_path = Path(zip_path)
    if isinstance(extract_to, str):
        extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)
    extracted_files = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.infolist():
            zip_ref.extract(member, extract_to)
            logger.info(f"Extracted: [{member.filename}]")
            extracted_files.append(f"{extract_to}/{member.filename}")
    return extracted_files


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


def _read_cstring(f) -> bytes:
    """Read a null-terminated byte string from the current position."""
    out = bytearray()
    while True:
        b = f.read(1)
        if not b:  # EOF
            break
        if b == b"\x00":  # terminator
            break
        out += b
    return bytes(out)


def parse_gzip_header(path: str | Path) -> dict[str, Any]:
    """
    Parse the gzip header at the beginning of `path` (first member only).

    Raises ValueError if file doesn't look like gzip.

    Args:
        path: Path to gzip file

    Returns:
        dict: Returns a dict with keys
                  - compression_method (int)
                  - flags (int)
                  - mtime (int, Unix epoch or 0)
                  - xflags (int)
                  - os (int)
                  - original_name (Optional[str])   # FNAME
                  - comment      (Optional[str])    # FCOMMENT
                  - header_end_offset (int)         # file offset where compressed data starts
    """
    p = Path(path)
    with p.open("rb") as f:
        # Magic
        if f.read(2) != b"\x1f\x8b":
            raise ValueError(f"{p} is not a gzip file (bad magic)")

        method_b = f.read(1)
        flags_b = f.read(1)
        if not method_b or not flags_b:
            raise ValueError("Truncated header")

        compression_method = method_b[0]
        flags = flags_b[0]

        # MTIME(4), XFL(1), OS(1)
        mtime_bytes = f.read(4)
        if len(mtime_bytes) != 4:
            raise ValueError("Truncated header (mtime)")
        mtime = struct.unpack("<I", mtime_bytes)[0]
        xflags = f.read(1)[0]
        os_code = f.read(1)[0]

        # Optional fields in order
        if flags & FEXTRA:
            xlen_bytes = f.read(2)
            if len(xlen_bytes) != 2:
                raise ValueError("Truncated FEXTRA length")
            xlen = struct.unpack("<H", xlen_bytes)[0]
            _ = f.read(xlen)  # skip payload

        original_name: Optional[str] = None
        if flags & FNAME:
            # Historically ISO-8859-1; utf-8 with replace is pragmatic
            original_name = _read_cstring(f).decode("utf-8", errors="replace")

        comment: Optional[str] = None
        if flags & FCOMMENT:
            comment = _read_cstring(f).decode("utf-8", errors="replace")

        if flags & FHCRC:
            _ = f.read(2)  # skip header CRC16

        return {
            "compression_method": compression_method,
            "flags": flags,
            "mtime": mtime,
            "xflags": xflags,
            "os": os_code,
            "original_name": original_name,
            "comment": comment,
            "header_end_offset": f.tell(),
        }
