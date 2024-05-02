# Scripts

This folder is dedicated to scripts, whether python, bash or sbatch.

Generally, scripts are more for standalone processes while figuring them out.

Once a script is more mature, it should be generalized and integrated into the package
itself.

## Scripts

| Scripts                   | Description                                                                                                                                                                                                                                                                 |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `resample_tiff_raster.py` | Script to resample a target tiff image, so it matches a source image's grid size and area. Resampling strategy is using a Nearest Neighbor algorythm to keep original values. <br/><br/>Use the scripts CLI for more information : `python3 resample_tiff_raster.py --help` |
