import os
import pathlib

import click
import rasterio
from rasterio.warp import Resampling
from rasterio.windows import from_bounds

from geospatial_tools import DATA_DIR

PROJECT_DATA_DIR = pathlib.Path(os.getenv("BASE_DATA_PATH", DATA_DIR))


def get_source_information(source_image):
    with rasterio.open(source_image) as source:
        # Save a lot of the information that is needed, so ortho image can be closed and
        # we can save space
        source_transform = source.transform
        source_crs = source.crs
        source_height = source.height
        source_width = source.width
        source_bounds = source.bounds
    return source_bounds, source_crs, source_height, source_transform, source_width


@click.command(context_settings={"show_default": True})
@click.option(
    "--source-image",
    type=str,
    help="Path of the source/reference image",
)
@click.option(
    "--resample-target",
    type=str,
    help="Path of the resampled image",
)
@click.option(
    "--output-path",
    type=str,
    help="Base output path",
    default=PROJECT_DATA_DIR,
)
def resample_tiff(source_image: str, resample_target: str, output_path: str):
    source_image = pathlib.Path(source_image)
    resample_target = pathlib.Path(resample_target)
    output_path = pathlib.Path(output_path)

    source_bounds, source_crs, source_height, source_transform, source_width = get_source_information(source_image)

    with rasterio.open(resample_target) as resample:
        resample_target_crs = resample.crs

        print("Check if CRS match")
        # Check if CRS match
        if resample_target_crs != source_crs:
            raise ValueError("CRS does not match, reproject 'source' to match 'target'")

        print("Creating window to clip dsm ortho")
        window = from_bounds(*source_bounds, transform=resample.transform)

        # Prepare to resample the source image
        kwargs = resample.meta.copy()
        kwargs.update(
            {"crs": resample_target_crs, "transform": source_transform, "width": source_width, "height": source_height}
        )

        print("Resampling dsm ortho")
        with rasterio.open(output_path / "resampled_dsm_ortho.tif", "w", **kwargs) as resampled:
            # Sample didn't include more than 1 band, but just in case...
            for i in range(1, resample.count + 1):
                # Read each band from the source and resample it
                resampled_band = resample.read(
                    i,
                    window=window,
                    out_shape=(source_height, source_width),
                    resampling=Resampling.nearest,
                    out_dtype="float32",
                )
                resampled.write(resampled_band, i)


if __name__ == "__main__":
    resample_tiff()  # pylint: disable=no-value-for-parameter
