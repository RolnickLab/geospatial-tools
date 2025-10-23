import gzip
import shutil
from pathlib import Path
from typing import Any, Generator

import numpy as np
import pandas as pd
import xarray as xr
from iris.analysis import MEAN
from iris.cube import Cube, CubeList
from iris.fileformats import netcdf
from iris.fileformats.nimrod import load_cubes

from geospatial_tools.utils import parse_gzip_header

FIVE_MIN = np.timedelta64(5, "m")


def extract_nimrod_from_archive(archive_file_path: str | Path, output_directory: str | Path = None) -> Path:
    """
    Extract nimrod data from an archive file. If no output directory is provided, the extracted data will be saved to
    the archive file's directory.

    Args:
        archive_file_path: Path to the archive file
        output_directory: Optional output directory.

    Returns:
            Path to the extracted nimrod data file
    """
    if isinstance(archive_file_path, str):
        archive_file_path = Path(archive_file_path)
    full_path = archive_file_path.resolve()
    parent_folder = archive_file_path.parent
    filename = archive_file_path.stem

    target_folder = None
    if output_directory:
        if isinstance(output_directory, str):
            output_directory = Path(output_directory)
        target_folder = output_directory

    if not target_folder:
        target_folder = parent_folder / filename

    target_folder.mkdir(parents=True, exist_ok=True)
    gzip_file_headers = parse_gzip_header(archive_file_path)
    contained_filename = gzip_file_headers["original_name"]

    with gzip.open(full_path, "rb") as f_in:
        if not contained_filename:
            contained_filename = filename
        print(f"Filename {contained_filename}")
        out_path = target_folder / contained_filename

        with open(out_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return out_path


def load_nimrod_cubes(filenames: list[str | Path]) -> Generator[Cube | Any, Any, None]:
    """

    Args:
        filenames:
        output_name:

    Returns:

    """
    cubes = load_cubes(filenames)
    # cubes = CubeList(cubes)
    # merged_cubes = cubes.merge_cube()
    # mean_cube = merged_cubes.collapsed("time", MEAN)
    # netcdf.save(mean_cube, output_name)
    # print(mean_cube)
    return cubes


def load_nimrod_from_archive(filename):
    """

    Args:
        filename:

    Returns:

    """
    nimrod_extracted_folder = extract_nimrod_from_archive(filename)
    file_list = nimrod_extracted_folder.glob("*")
    cubes = load_nimrod_cubes(file_list)
    return cubes


def merge_nimrod_cubes(cubes):
    """

    Args:
        cubes:

    Returns:

    """
    cubes = CubeList(cubes)
    merged_cubes = cubes.merge_cube()
    mean_cube = merged_cubes.collapsed("time", MEAN)
    return mean_cube


def write_cube_to_file(cube, output_name):
    """
    Save a nimrod cube to a Netcdf file.

    Args:
        cube:
        output_name:

    Returns:
    """
    netcdf.save(cube, output_name)


def assert_dataset_time_dim_is_valid(dataset: xr.Dataset, time_dimension_name: str = "time") -> None:
    """
    Ths function checks that the time dimension of a given dataset :
        - Is composed of 5-minute time bins - Which is the native Nimrod format
        - Contains a continuous time series, without any holes - which would lead to false statistics when resampling

    Args:
        dataset: Merged nimrod cube
        time_dimension_name: Name of the time dimension

    Returns:
        Bool value indicating if the time bins are 5 minutes long and if there are no
        gaps in the time series
    """
    dataset_time_dimension = dataset[time_dimension_name]
    if not dataset_time_dimension.to_index().is_monotonic_increasing:
        raise AssertionError("Time is not sorted ascending")
    if not dataset_time_dimension.to_index().is_unique:
        duplicates = dataset_time_dimension.to_index()[dataset_time_dimension.to_index().duplicated(keep=False)]
        raise AssertionError(f"Duplicate timestamps present: {duplicates[:10]} ...")

    difference_between_timesteps = dataset_time_dimension.diff(time_dimension_name)
    if (difference_between_timesteps != FIVE_MIN).any():
        larger_time_gaps = np.nonzero((difference_between_timesteps != FIVE_MIN).compute())[0][:5]
        raise AssertionError(
            f"Non-5min gaps at positions {larger_time_gaps} "
            f"(examples: {difference_between_timesteps.isel({time_dimension_name: larger_time_gaps}).values})"
        )

    start = pd.Timestamp(dataset_time_dimension.values[0])
    end = pd.Timestamp(dataset_time_dimension.values[-1])
    expected_index = pd.date_range(start=start, end=end, freq="5min", inclusive="both")
    dataset_index = dataset_time_dimension.to_index()
    missing_indexes = expected_index.difference(dataset_index)
    if len(missing_indexes) > 0:
        raise AssertionError(f"missing {len(missing_indexes)} stamps; first few: {missing_indexes[:10]}")


def resample_nimrod_timebox_30min_bins(filenames, output_name):
    """
    This will resample nimrod data's bins to 30-minute interval instead of their
    normal 5-minute interval. It uses a mean resampling, and creates time bins like
    follows :

    ex. [[09h00, < 9h05], [09h05, < 9h10], ... ] -> [[09h00, < 9h30], [09h30, < 10h], ... ]

    Args:
        filenames:
        output_name:

    Returns:

    """
    ds = xr.open_mfdataset(filenames, combine="nested", concat_dim="time")
    ds_30min = ds.resample(time="30min").mean()
    ds_30min.to_netcdf(output_name)


extract_nimrod_from_archive(
    "/home/francispelletier/projects/geospatial_tools/data/metoffice-c-band-rain-radar_uk_20180101_1km-composite.dat.gz/metoffice-c-band-rain-radar_uk_201801012355_1km-composite.dat.gz"
)
# cubes = load_nimrod_cubes(
#     filenames="/home/francispelletier/projects/geospatial_tools/data/metoffice-c-band-rain-radar_uk_20180101_1km-composite.dat.gz/metoffice-c-band-rain-radar_uk_201801012355_1km-composite.dat/metoffice-c-band-rain-radar_uk_201801012355_1km-composite.dat",
#     output_name="nimrod_cubes_30min")
# for cube in cubes:
#     print(cube)
