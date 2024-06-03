import json
import logging
import pathlib
import sys

import yaml

from geospatial_tools import CONFIG

GEOPACKAGE_DRIVER = "GPKG"


def create_logger(logger_name: str) -> logging.Logger:
    """Creates a logger object using input name parameter that outputs to stdout.

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
    """This function takes in the path, or name of the file if it can be found in the config/ folder,
    with of without the extension, and returns the values of the file in a dictionary format.

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
        CONFIG / yaml_config_file,
        CONFIG / f"{yaml_config_file}.yaml",
        CONFIG / f"{yaml_config_file}.yml",
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
    """This function takes in the path, or name of the file if it can be found in the config/ folder,
    with of without the extension, and returns the values of the file in a dictionary format.

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
        CONFIG / json_config_file,
        CONFIG / f"{json_config_file}.json",
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
