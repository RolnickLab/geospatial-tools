from pathlib import Path

from geospatial_tools import DATA_DIR
from geospatial_tools.utils import download_url, get_yaml_config, unzip_file

# See configs/data_file_links.yaml - these keys need to match
USA_POLYGON = "united_states_polygon"
SENTINEL_2_TILLING_GRID = "sentinel_2_tiling_grid"


def _download_from_link(
    target_download: str, output_name: str = None, output_directory: str | Path = DATA_DIR
) -> list[str | Path]:
    file_configs = get_yaml_config("data_file_links")
    key = target_download
    url = file_configs[key]["url"]
    if not output_name:
        output_name = key

    output_path = f"{output_directory}/{output_name}.zip"
    downloaded_file = download_url(url=url, filename=output_path)
    file_list = unzip_file(downloaded_file, extract_to=output_directory)
    downloaded_file.unlink()
    return file_list


def download_usa_polygon(output_name: str = USA_POLYGON, output_directory: str | Path = DATA_DIR) -> list[str | Path]:
    """
    Download USA polygon file.

    Parameters
    ----------
    output_name
        What name to give to downloaded file
    output_directory
        Where to save the downloaded file

    Returns
    -------
    List of output path to downloaded file
    """
    file_list = _download_from_link(
        target_download=USA_POLYGON, output_name=output_name, output_directory=output_directory
    )
    return file_list


def download_s2_tiling_grid(
    output_name: str = SENTINEL_2_TILLING_GRID, output_directory: str | Path = DATA_DIR
) -> list[str | Path]:
    """
    " Download Sentinel 2 tiling grid file.

    Parameters
    ----------
    output_name
        What name to give to downloaded file
    output_directory
        Where to save the downloaded file

    Returns
    -------
    List of output path to downloaded file
    """
    file_list = _download_from_link(
        target_download=SENTINEL_2_TILLING_GRID, output_name=output_name, output_directory=output_directory
    )
    return file_list
