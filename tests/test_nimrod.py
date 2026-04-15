import shutil
from pathlib import Path

import iris
import pandas as pd
import pytest
import xarray as xr
from iris.cube import Cube

from geospatial_tools.radar.nimrod import (
    assert_dataset_time_dim_is_valid,
    extract_nimrod_from_archive,
    load_nimrod_cubes,
    load_nimrod_from_archive,
    mean_nimrod_cubes,
    merge_nimrod_cubes,
    resample_nimrod_timebox_30min_bins,
    write_cube_to_file,
)

# --- Fixtures ---


@pytest.fixture
def nimrod_test_files():
    """Returns a list of paths to the nimrod test resources."""
    resource_dir = Path(__file__).parent / "resources" / "nimrod"
    return sorted(resource_dir.glob("*.gz"))


@pytest.fixture
def extracted_nimrod_files(nimrod_test_files, tmp_path):
    """Extracts nimrod files to a temp directory and returns their paths."""
    extracted_paths = []
    for archive_path in nimrod_test_files:
        dest_path = extract_nimrod_from_archive(archive_path, output_directory=tmp_path)
        extracted_paths.append(dest_path)
    return extracted_paths


@pytest.fixture
def sample_merged_cube(extracted_nimrod_files):
    """Returns a merged cube from the test files."""
    cubes = list(load_nimrod_cubes(extracted_nimrod_files))
    return merge_nimrod_cubes(cubes)


# --- Tests ---


def test_extract_nimrod_from_archive(nimrod_test_files, tmp_path) -> None:
    """Test extracting a nimrod file from a gzip archive."""
    archive_file = nimrod_test_files[0]
    output_dir = tmp_path / "output"

    extracted_path = extract_nimrod_from_archive(archive_file, output_directory=output_dir)

    assert extracted_path.exists()
    assert extracted_path.parent == output_dir

    with open(extracted_path, "rb") as f:
        header = f.read(2)
    assert header != b"\x1f\x8b"


def test_extract_nimrod_from_archive_no_output_dir(nimrod_test_files, tmp_path) -> None:
    """
    Test extraction defaults to parent folder when no output dir is specified.

    Note: We copy the source file to tmp_path first to avoid polluting the source directory.
    """
    archive_source = nimrod_test_files[0]
    archive_in_tmp = tmp_path / archive_source.name
    shutil.copy(archive_source, archive_in_tmp)

    extracted_path = extract_nimrod_from_archive(archive_in_tmp)

    assert extracted_path.exists()
    assert extracted_path.parent == tmp_path / archive_in_tmp.stem


def test_load_nimrod_cubes(extracted_nimrod_files) -> None:
    """Test loading cubes from extracted files."""
    cubes_gen = load_nimrod_cubes(extracted_nimrod_files)
    cubes = list(cubes_gen)

    assert len(cubes) == len(extracted_nimrod_files)
    assert all(isinstance(c, Cube) for c in cubes)


def test_load_nimrod_from_archive(nimrod_test_files, tmp_path) -> None:
    """Test loading cubes directly from an archive (which handles extraction)."""

    archive_file = nimrod_test_files[0]

    archive_in_tmp = tmp_path / archive_file.name
    shutil.copy(archive_file, archive_in_tmp)

    cubes_gen = load_nimrod_from_archive(archive_in_tmp)
    cubes = list(cubes_gen)

    assert len(cubes) >= 1
    assert isinstance(cubes[0], Cube)


def test_merge_nimrod_cubes(extracted_nimrod_files) -> None:
    """Test merging a list of nimrod cubes."""
    cubes = list(load_nimrod_cubes(extracted_nimrod_files))
    assert len(cubes) > 1

    merged_cube = merge_nimrod_cubes(cubes)

    assert isinstance(merged_cube, Cube)

    time_coord = merged_cube.coord("time")
    assert len(time_coord.points) == len(cubes)


def test_mean_nimrod_cubes(sample_merged_cube) -> None:
    """Test calculating the mean over time."""
    mean_cube = mean_nimrod_cubes(sample_merged_cube)

    assert isinstance(mean_cube, Cube)

    original_shape = sample_merged_cube.shape
    mean_shape = mean_cube.shape

    assert mean_shape == original_shape[1:]


def test_write_cube_to_file(sample_merged_cube, tmp_path) -> None:
    """Test writing a cube to a NetCDF file."""
    output_file = tmp_path / "test_output.nc"
    write_cube_to_file(sample_merged_cube, output_file)

    assert output_file.exists()
    loaded = iris.load_cube(str(output_file))
    assert loaded is not None


def test_assert_dataset_time_dim_is_valid() -> None:
    """Test the time dimension validation logic."""

    # Case 1: Valid 5-min data
    times = pd.date_range("2023-01-01 10:00", periods=5, freq="5min")
    ds_valid = xr.Dataset({"data": (("time",), [1, 2, 3, 4, 5])}, coords={"time": times})

    assert_dataset_time_dim_is_valid(ds_valid)

    # Case 2: Non-monotonic
    times_unsorted = [times[0], times[2], times[1]]
    ds_unsorted = xr.Dataset({"data": (("time",), [1, 2, 3])}, coords={"time": times_unsorted})
    with pytest.raises(AssertionError, match="Time is not sorted ascending"):
        assert_dataset_time_dim_is_valid(ds_unsorted)

    # Case 3: Duplicates
    times_dup_adj = [times[0], times[0], times[1]]
    ds_dup_adj = xr.Dataset({"data": (("time",), [1, 2, 3])}, coords={"time": times_dup_adj})

    with pytest.raises(AssertionError, match="Duplicate timestamps present"):
        assert_dataset_time_dim_is_valid(ds_dup_adj)

    # Case 4: Gaps (missing 5 min)
    times_gap = [times[0], times[1], times[3]]
    ds_gap = xr.Dataset({"data": (("time",), [1, 2, 3])}, coords={"time": times_gap})

    with pytest.raises(AssertionError, match="Non-5min gaps"):
        assert_dataset_time_dim_is_valid(ds_gap)


def test_time_dim_valid_with_nimrod_data(sample_merged_cube, tmp_path) -> None:
    """Test the time dimension validation logic with sample nimrod data."""

    nc_file = tmp_path / "input_for_tim_dim.nc"
    write_cube_to_file(sample_merged_cube, nc_file)
    with xr.open_dataset(nc_file) as ds:
        assert_dataset_time_dim_is_valid(ds)


def test_resample_nimrod_timebox_30min_bins(sample_merged_cube, tmp_path) -> None:
    """Test resampling to 30 minute bins."""

    nc_file = tmp_path / "input_for_resample.nc"
    write_cube_to_file(sample_merged_cube, nc_file)

    output_resampled = tmp_path / "resampled_30min.nc"

    resample_nimrod_timebox_30min_bins([str(nc_file)], output_resampled)

    assert output_resampled.exists()

    with xr.open_dataset(output_resampled) as ds:
        # There are 12 nimrod files, so we expect 2 time steps (00:00 and 00:30)
        assert len(ds["time"]) == 2
