import calendar
import datetime
import json
import logging
import pathlib
import sys
from typing import Union

import requests
import yaml
from rasterio import CRS

from geospatial_tools import CONFIGS

GEOPACKAGE_DRIVER = "GPKG"


def create_logger(logger_name: str) -> logging.Logger:
    """
    Creates a logger object using input name parameter that outputs to stdout.

    Parameters
    ----------
    logger_name : str
        Name of logger

    Returns
    -------
    logging.Logger
        Created logger object
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-10.10s [%(threadName)s][%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOGGER = create_logger(__name__)


def get_yaml_config(yaml_config_file: str, logger=LOGGER) -> dict:
    """
    This function takes in the path, or name of the file if it can be found in the config/ folder, with of without the
    extension, and returns the values of the file in a dictionary format.

    Ex. For a file named app_config.yml (or app_config.yaml), directly in the config/ folder,
        the function could be called like so : `params = get_yaml_config('app_config')`

    Parameters
    ----------
    yaml_config_file : str
        Path to yaml config file. If config file is in the config folder,
        you can use the file's name without the extension.
    logger : _type_, optional
        Logger to handle messaging, by default LOGGER

    Returns
    -------
    dict
        Dictionary of YAML configuration values
    """

    potential_paths = [
        pathlib.Path(yaml_config_file),
        CONFIGS / yaml_config_file,
        CONFIGS / f"{yaml_config_file}.yaml",
        CONFIGS / f"{yaml_config_file}.yml",
    ]

    config_filepath = None
    for path in potential_paths:
        if path.exists():
            config_filepath = path
            logger.info(f"Yaml config file [{str(path)}] found.")
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

    Parameters
    ----------
    json_config_file : str
        Path to JSON config file. If config file is in the config folder,
    logger : _type_, optional
        Logger to handle messaging, by default LOGGER

    Returns
    -------
    dict
        Dictionary of JSON configuration values
    """

    potential_paths = [
        pathlib.Path(json_config_file),
        CONFIGS / json_config_file,
        CONFIGS / f"{json_config_file}.json",
    ]

    config_filepath = None
    for path in potential_paths:
        if path.exists():
            config_filepath = path
            logger.info(f"JSON config file [{str(path)}] found.")
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


def create_crs(dataset_crs: Union[str, int], logger=LOGGER):
    """

    Parameters
    ----------
    dataset_crs : Union[str, int]
        EPSG code in string or int format. Can be given in the following ways: 5070 | "5070" | "EPSG:5070"
    logger:
        Logger instance

    Returns
    -------
    target_crs : str
        EPSG code in string format : EPSG:<numerical_code>

    """
    logger.info(f"Attempting to create EPSG code from following input : [{dataset_crs}]")
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


def download_url(url, filename):
    response = requests.get(url, timeout=None)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {filename} successfully.")
        return filename

    print(f"Failed to download the asset. Status code: {response.status_code}")
    return None


def create_date_range_for_specific_period(
    start_year: int, end_year: int, start_month_range: int, end_month_range: int
) -> list[datetime.datetime]:
    """
    This function create a list of date ranges.

    For example, I want to create date ranges for 2020 and 2021, but only for the months from March to May.
    I therefore expect to have 2 ranges: [2020-03-01 to 2020-05-30, 2021-03-01 to 2021-05-30].

    Handles the automatic definition of the last day for the end month, as well as periods that cross over years

    For example, I want to create date ranges for 2020 and 2022, but only for the months from November to January.
    I therefore expect to have 2 ranges: [2020-11-01 to 2021-01-31, 2021-11-01 to 2022-01-31].

    Parameters
    ----------
    start_year : int
        Start year for ranges
    end_year : int
        End year for ranges
    start_month_range : int
        Starting month for each period
    end_month_range : int
        End month for each period (inclusively)

    Returns
    -------
    list[datatime.datetime]
        Dictionary containing datatime data ranges
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
